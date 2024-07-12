from __future__ import annotations

import warnings
from collections import Counter

from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from typesense import Client
from typesense import exceptions as typesense_exceptions
from typing_extensions import Literal


class TypesenseCollection:
    """Class for mapping a Django model to a Typesense collection."""

    def __init__(
        self,
        *,
        client: Client,
        model: models.Model,
        index_fields: set[models.Field] = None,
        parents: set[models.Field] = None,
        children: set[models.Field] = None,
        facets: set[models.Field] | Literal[True] = None,
        detailed_parents: set[models.Field] | Literal[True] = None,
        detailed_children: set[models.Field] | Literal[True] = None,
    ) -> None:
        """
        Initializes a new instance of TypesenseCollection.

        :param client: An instance of Client to interact with the Typesense API.
        :param model: The Django model that this instance is associated with.
        :param index_fields: A set of model fields to be indexed. Defaults to None,
          meaning all fields are indexed.
        :param parents: A set of model fields representing parent relations. Defaults to None.
        :param children: A set of model fields representing child relations. Defaults to None.
        :param facets: A set of model fields to be used as facets, or True to include all.
            Defaults to None.
        :param detailed_parents: A set of model fields for which detailed parent information
          is required, mapping them to `object`, or True to include all. Defaults to None.
        :param detailed_children: A set of model fields for which detailed child information
          is required, mapping them to `object[]`, or True to include all. Defaults to None.

        """
        self.index_fields = index_fields or set()
        self.children = children or set()
        self.facets = facets or set()
        self.parents = parents or set()
        self.detailed_parents = detailed_parents or set()
        self.detailed_children = detailed_children or set()
        self.model = model
        self.client = client
        self._validate_client_and_model()
        self._handle_all()

    def _validate_client_and_model(self):
        if not isinstance(self.client, Client):
            raise typesense_exceptions.ConfigError(
                'Client must be an instance of Typesense Client.',
            )
        if not issubclass(self.model, models.Model):
            raise typesense_exceptions.ConfigError(
                'Model must be an instance of the default models.Model class.',
            )

    def _handle_all(self):
        self._handle_name()
        self._handle_fields()
        self._handle_facets()
    def _handle_name(self) -> None:
        """Handle name."""
        if not self.model._meta.verbose_name:
            raise typesense_exceptions.RequestMalformed('Model name is empty.')
        self.name = self.model._meta.verbose_name

    def _handle_fields(self) -> None:
        if (
            not self.index_fields
            and not self.parents
            and not self.children
        ):
            self._handle_implicit_fields()
            return

        self._handle_explicit_fields()

    def _handle_explicit_fields(self) -> None:
        """Handle explicit fields."""
        self._handle_relations_in_index_fields()
        self._handle_mismatched_fields()
        self._handle_multiple_of_same_field_name()
        self._handle_explicit_relations()
    def _handle_relations_in_index_fields(self) -> None:
        """Handle relations in index fields."""
        relations = self._get_relations_in_index_fields()
        if relations:
            raise typesense_exceptions.RequestMalformed(
                'Relations {relations} are not allowed in index fields.'.format(
                    relations=relations,
                ),
            )

    def _get_relations_in_index_fields(self) -> set[models.Field]:
        return {field for field in self.index_fields if field.is_relation}

    def _handle_explicit_relations(self) -> None:
        """Handle explicit references."""
        mismatched_references, mismatched_referenced_by = (
            self._get_mismatched_relations()
        )
        if mismatched_references:
            raise typesense_exceptions.RequestMalformed(
                'Model {model} has no foreign relations {relations}.'.format(
                    model=self.model._meta.model,
                    relations=mismatched_references,
                ),
            )

        if mismatched_referenced_by:
            raise typesense_exceptions.RequestMalformed(
                'Model {model} has no foreign relations {relations}.'.format(
                    model=self.model._meta.model,
                    relations=mismatched_referenced_by,
                ),
            )

    def _get_mismatched_relations(self) -> Tuple[set[models.Field], set[models.Field]]:
        model_references: set[models.ForeignKey] = set()
        model_referenced_by: set[models.Field] = set()

        for field in self.model._meta.get_fields():
            if field.many_to_one:
                model_references.add(field)
            if field.one_to_many:
                model_referenced_by.add(field)

        mismatched_references = self.parents - model_references
        mismatched_referenced_by = self.children - model_referenced_by

        return mismatched_references, mismatched_referenced_by

    def _handle_multiple_of_same_field_name(self) -> None:
        """Handle multiple of the same field name."""
        if self._has_multiple_of_same_field_name():
            raise typesense_exceptions.RequestMalformed('Field names must be unique.')

    def _has_multiple_of_same_field_name(self) -> bool:
        field_name_counts = Counter(field.name for field in self.index_fields)
        return any(count > 1 for count in field_name_counts.values())

    def _handle_mismatched_fields(self) -> None:
        """Handle mismatched fields."""
        mismatched_fields = self._get_mismatched_fields()

        if mismatched_fields:
            warnings.warn(
                'Some fields: {fields} are not present in the model.'.format(
                    fields=mismatched_fields,
                ),
                UserWarning,
                stacklevel=2,
            )

    def _get_mismatched_fields(self) -> set[models.Field]:
        """Get the fields that are not present in the model."""
        model_fields = {
            field for field in self.model._meta.get_fields() if not field.is_relation
        }
        return self.index_fields - model_fields

    def _handle_implicit_fields(self) -> None:
        for field in self.model._meta.get_fields():
            if not isinstance(field, (models.Field, ForeignObjectRel)):
                continue
            if not field.is_relation:
                self.index_fields.add(field)

            self._handle_relation_field(field)

    def _handle_relation_field(
        self,
        field: models.Field,
    ) -> None:
        if field.related_model is self.model:
            raise typesense_exceptions.RequestMalformed('Model cant reference itself.')

        if field.many_to_many:
            raise typesense_exceptions.RequestMalformed(
                'Implicit Many to many field {field} is not allowed.'.format(
                    field=field,
                ),
            )
        if field.many_to_one:
            self._handle_many_to_one(field)
        elif field.one_to_many:
            self._handle_one_to_many(field)

    def _handle_many_to_one(
        self,
        field: models.Field,
    ) -> None:
        self.parents.add(field)

    def _handle_one_to_many(
        self,
        field: models.Field,
    ) -> None:
        self.children.add(field)

    def _handle_facets(self) -> None:
        """Handle facets."""
        facetable_fields = self.index_fields.union(self.parents)

        if self.facets is True:
            self.facets = facetable_fields

        if not self.facets.issubset(facetable_fields):
            raise typesense_exceptions.RequestMalformed(
                'Facets must be a subset of index fields.',
            )

        if self.facets.intersection(self.parents) and not self.use_joins:
            warnings.warn(
                'Facetting on relation only affects JOINs',
                UserWarning,
                stacklevel=2,
            )

    def _handle_detailed_relations(self) -> None:
        """Handle detailed relations."""
        if self.detailed_parents is True:
            self.detailed_parents = self.parents
        if self.detailed_children is True:
            self.detailed_children = self.children

        if not self.detailed_parents.issubset(self.parents):
            raise typesense_exceptions.RequestMalformed(
                'Detailed references must be a subset of references.',
            )

        if not self.detailed_children.issubset(self.children):
            raise typesense_exceptions.RequestMalformed(
                'Detailed referenced by must be a subset of referenced by.',
            )

