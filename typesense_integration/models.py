from __future__ import annotations

import warnings
from collections import Counter
from typing import Tuple

from typing import (
    Any,
    ClassVar,
    NotRequired,
    Tuple,
    TypedDict,
    Union,
    Unpack,
)

from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from typesense import Client
from typesense import exceptions as typesense_exceptions
from typing_extensions import Literal

from typesense_integration.common.utils import ensure_is_subset_or_all, snake_case


class CollectionParams(TypedDict):
    """
    :py:class:`CollectionParams` represents the parameters for creating a Typesense collection.

    :param client: An instance of Client to interact with the Typesense API.
    :param model: The Django model that this instance is associated with.
    :param index_fields: A set of model fields to be indexed. Defaults to None,
        meaning all fields are indexed.
    :param skip_index_fields: A set of model fields to not be indexed and instead saved
        on disk. Defaults to None, meaning all fields are indexed.
    :param parents: A set of model fields representing parent relations. Defaults to None.
    :param default_sorting_field: The default sorting field for the collection.
        Defaults to None.
    :param geopoints: A set of model fields representing geopoints. Should not be included
        in `index_fields`. Defaults to None.
    :param children: A set of model fields representing child relations. Defaults to None.
    :param facets: A set of model fields to be used as facets, or True to include all.
        Defaults to None.
    :param detailed_parents: A set of model fields for which detailed parent information
        is required, mapping them to `object`, or True to include all. Defaults to None.
    :param detailed_children: A set of model fields for which detailed child information
        is required, mapping them to `object[]`, or True to include all. Defaults to None.
    :param use_joins: A boolean indicating whether to use joins for relations.
        Defaults to False.
    :param override_id: A boolean indicating whether to override the default Typesense ID
        field. Defaults to False. Not needed if the model's `id` field is passed as an
        index field.

    """

    client: Client
    model: type[models.Model]
    index_fields: NotRequired[set[models.Field[Any, Any]]]
    skip_index_fields: NotRequired[
        set[models.Field[Any, Any] | models.ForeignObjectRel]
    ]
    parents: NotRequired[set[models.ForeignKey[models.Model, models.Model]]]
    geopoints: NotRequired[set[Geopoint]]
    children: NotRequired[set[models.ManyToOneRel]]
    facets: NotRequired[
        set[models.Field[Any, Any] | models.ForeignKey[models.Model, models.Model]]
        | Literal[True]
    ]
    detailed_parents: NotRequired[
        set[models.ForeignKey[models.Model, models.Model]] | Literal[True]
    ]
    detailed_children: NotRequired[set[models.ManyToOneRel] | Literal[True]]
    default_sorting_field: NotRequired[
        models.IntegerField[Any, Any]
        | models.FloatField[Any, Any]
        | models.DecimalField[Any, Any]
        | None
    ]
    use_joins: NotRequired[bool]
    override_id: NotRequired[bool]


class APIField(TypedDict):
    """
    Typesense API field schema.

    Part of the `fields` key in the Typesense schema.
    https://typesense.org/docs/26.0/api/collections.html#schema-parameters

    :param name: The name of the field.
    :param type: The type of the field.
    :param facet: Whether the field is a facet.
      https://typesense.org/docs/26.0/api/search.html#facet-results
    :param index: Whether the field is indexed.
    :param reference: The reference field for a relation.
      https://typesense.org/docs/26.0/api/joins.html#joins

    """

    name: str
    type: str
    facet: NotRequired[bool]
    index: NotRequired[bool]
    reference: NotRequired[str]
    optional: NotRequired[bool]


class APICollection(TypedDict):
    """

    Typesense API collection schema.

    https://typesense.org/docs/26.0/api/collections.html#schema-parameters

    :param name: The name of the collection.
    :param fields: A list of fields in the collection.
    :param default_sorting_field: The default sorting field.
    :param enable_nested_fields: Whether nested fields are enabled.
    :param token_separators: Token separators for the collection.

    """

    name: str
    fields: list[APIField]
    default_sorting_field: NotRequired[str]
    enable_nested_fields: NotRequired[bool]
    token_separators: NotRequired[list[str]]


Geopoint = Union[
    Tuple[
        models.FloatField[Any, Any] | models.DecimalField[Any, Any],
        models.FloatField[Any, Any] | models.DecimalField[Any, Any],
    ],
]


class TypesenseCollection:
    """Class for mapping a Django model to a Typesense collection."""

    mapped_geopoint_types: ClassVar[set[type[models.Field[Any, Any]]]] = {
        models.FloatField,
        models.DecimalField,
    }

    mapped_sortable_types: ClassVar[set[type[models.Field[Any, Any]]]] = {
        models.FloatField,
        models.DecimalField,
        models.IntegerField,
    }

    # TODO: add image search
    mapped_field_types: ClassVar[dict[type[models.Field[Any, Any]], str]] = {
        models.AutoField: 'int32',
        models.CharField: 'string',
        models.URLField: 'string',
        models.TextField: 'string',
        models.IntegerField: 'int32',
        models.BigIntegerField: 'int64',
        models.PositiveBigIntegerField: 'int64',
        models.PositiveSmallIntegerField: 'int32',
        models.PositiveIntegerField: 'int32',
        models.SlugField: 'string',
        models.FloatField: 'float',
        models.BooleanField: 'bool',
        models.DateField: 'int64',
        models.DateTimeField: 'int64',
        models.DecimalField: 'float64',
        models.FloatField: 'float32',
        models.GenericIPAddressField: 'string',
        models.JSONField: 'string',
        models.SmallAutoField: 'int32',
        models.BigAutoField: 'int64',
        models.UUIDField: 'string',
        models.EmailField: 'string',
        models.FilePathField: 'string',
        models.SmallIntegerField: 'int32',
    }

    def __init__(self, **kwargs: Unpack[CollectionParams]) -> None:
        """Initializes a new instance of TypesenseCollection."""
        self.utils = TypesenseCollectionUtils
        self.client = kwargs.get('client')
        self.model = kwargs['model']
        self._validate_client_and_model()
        self._handle_all()

    def _validate_client_and_model(self):
        self.index_fields = kwargs.get('index_fields', set())
        self.skip_index_fields = kwargs.get('skip_index_fields', set())
        self.children = kwargs.get('children', set())
        self.parents = kwargs.get('parents', set())
        self.geopoints = kwargs.get('geopoints', set())
        self.use_joins = kwargs.get('use_joins', False)
        self.override_id = kwargs.get('override_id', False)
        self._handle_fields()

        self.facetable_fields = self.index_fields.union(self.parents)
        self.facets = ensure_is_subset_or_all(
            kwargs.get('facets', set()),
            self.facetable_fields,
        )

        self.detailed_children = ensure_is_subset_or_all(
            kwargs.get('detailed_children', set()),
            self.children,
        )
        self.detailed_parents = ensure_is_subset_or_all(
            kwargs.get('detailed_parents', set()),
            self.parents,
        )

        self._handle_facets()
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
        self._handle_typesense_fields()
        self._handle_typesense_relations()
        self._handle_typesense_geopoints()

    def _handle_name(self) -> None:
        """Handle name."""
        if not self.model._meta.verbose_name:
            raise typesense_exceptions.RequestMalformed('Model name is empty.')
        self.name = snake_case(self.model._meta.verbose_name)

    def _handle_fields(self) -> None:
        if (
            not self.index_fields
            and not self.parents
            and not self.children
            and not self.geopoints
        ):
            self._handle_implicit_fields()
            return

        self._handle_explicit_fields()

    def _handle_explicit_fields(self) -> None:
        """Handle explicit fields."""
        self._handle_relations_in_index_fields()
        self._handle_geopoints_in_index_fields()
        self._handle_mismatched_fields()
        self._handle_multiple_of_same_field_name()
        self._handle_explicit_relations()
        self._handle_geopoints()

    def _handle_geopoints_in_index_fields(self) -> None:
        """Handle geopoints."""
        if self._has_geopoints_in_index_fields():
            raise typesense_exceptions.RequestMalformed(
                'Geopoints are already present in index fields.',
            )

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

    def _has_geopoints_in_index_fields(self) -> set[models.Field]:
        for lat, long in self.geopoints:
            return lat in self.index_fields or long in self.index_fields

    def _handle_geopoints(self) -> None:
        """Handle geopoints."""
        for lat, long in self.geopoints:
            lat_type = lat.__class__ in self.mapped_geopoint_types
            long_type = long.__class__ in self.mapped_geopoint_types

            if not lat_type:
                raise typesense_exceptions.RequestMalformed(
                    'Geopoint {geopoint} is not supported. Supported types: \n {types}'.format(
                        geopoint=lat_type,
                        types=self.mapped_geopoint_types,
                    ),
                )
            if not long_type:
                raise typesense_exceptions.RequestMalformed(
                    'Geopoint {geopoint} is not supported. Supported types: \n {types}'.format(
                        geopoint=long_type,
                        types=self.mapped_geopoint_types,
                    ),
                )

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
            if self._validate_id_field(field):
                continue

            if not field.is_relation:
                self.index_fields.add(field)

            self._handle_relation_field(field)

    def _validate_id_field(self, field: models.Field) -> bool:
        return field.name == 'id' and not self.override_id

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

    def _handle_typesense_fields(self) -> None:
        """Handle Typesense fields."""
        self.typesense_fields = [
            {
                'name': field.name,
                'type': self._handle_typesense_field_type(field),
                **({'facet': True} if field in self.facets else {}),
            }
            for field in self.index_fields
        ]

    def _handle_typesense_geopoints(self) -> None:
        """Handle Typesense geopoints."""
        self.typesense_geopoints = [
            {
                'name': '{long}_{lat}'.format(long=long, lat=lat),
                'type': 'geopoint',
            }
            for long, lat in self.geopoints
        ]

    def _handle_typesense_field_type(self, field: models.Field) -> str:
        """Handle Typesense field type."""
        if field.name == 'id':
            return 'string'

        typesense_type = self.mapped_field_types.get(field.__class__)

        if typesense_type is None:
            raise typesense_exceptions.RequestMalformed(
                'Field type for {field} is not supported. Supported types: \n {types}'.format(
                    field=field,
                    types=self.mapped_field_types.keys(),
                ),
            )

        if isinstance(field, models.DecimalField):
            return self._handle_decimal_field(field)

        return typesense_type

    def _handle_decimal_field(self, field: models.DecimalField) -> str:
        """Handle DecimalField for different sizes."""
        max_float_value = 3.4e38
        # Calculate the maximum value that can be represented by the field
        max_field_value = (10 ** (field.max_digits - field.decimal_places)) - (
            10**-field.decimal_places
        )

        # Float32 can represent values up to ~3.4E+38,
        # but precision might be lost for values > 1E+7
        # Float64 can represent values up to ~1.7E+308,
        # with precision up to 15-17 decimal digits
        if max_field_value < max_float_value and field.decimal_places <= 7:
            return 'float32'

        return 'float64'

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

    def _handle_typesense_relations(self) -> None:
        """Handle Typesense relations."""
        self.typesense_relations = []

        self._handle_detailed_relations()

        if self.use_joins:
            for field in self.parents:
                self._handle_composite_foreign_key(field)

                _, related_field = field.related_fields[0]
                self.typesense_relations.append(
                    {
                        'name': '{local_field_name}_{field_related_name}'.format(
                            local_field_name=field.name,
                            field_related_name=related_field.name,
                        ),
                        'type': self._handle_typesense_field_type(related_field),
                        'reference': '{related_model_name}.{related_field_name}'.format(
                            related_model_name=snake_case(
                                field.related_model._meta.verbose_name,
                            ),
                            related_field_name=related_field.name,
                        ),
                        **({'facet': True} if field in self.facets else {}),
                    },
                )

        for reference in self.detailed_parents:
            self.typesense_relations.append(
                {
                    'name': reference.name,
                    'type': 'object',
                },
            )
        for child in self.detailed_children:
            self.typesense_relations.append(
                {
                    'name': child.name,
                    'type': 'object[]',
                },
            )

    def _handle_composite_foreign_key(self, field: models.Field) -> None:
        """Handle composite foreign keys."""
        if self._is_composite_foreign_key(field):
            raise typesense_exceptions.RequestMalformed(
                'Composite key {field} is not allowed'.format(field=field),
            )

    def _is_composite_foreign_key(self, field: models.Field) -> bool:
        return len(field.related_fields) > 1
