from __future__ import annotations

import warnings

from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from typesense import Client
from typesense import exceptions as typesense_exceptions


class TypesenseCollection:
    """Class for mapping a Django model to a Typesense collection."""

    def __init__(
        self,
        *,
        client: Client,
        model: models.Model,
        index_fields: set[models.Field] = None,
    ) -> None:
        """
        Initializes a new instance of TypesenseCollection.

        :param client: An instance of Client to interact with the Typesense API.
        :param model: The Django model that this instance is associated with.
        :param index_fields: A set of model fields to be indexed. Defaults to None,
          meaning all fields are indexed.
        """
        self.index_fields = index_fields or set()
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
        self._handle_fields()
    def _handle_fields(self) -> None:
        if (
            not self.index_fields
        ):
            self._handle_implicit_fields()
            return

        self._handle_explicit_fields()

    def _handle_explicit_fields(self) -> None:
        """Handle explicit fields."""
        self._handle_mismatched_fields()
        self._handle_multiple_of_same_field_name()

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

