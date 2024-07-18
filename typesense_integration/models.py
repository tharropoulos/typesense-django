from __future__ import annotations

import warnings
from typing import (
    Any,
    ClassVar,
    Iterable,
    NotRequired,
    Tuple,
    TypedDict,
    TypeGuard,
    TypeVar,
    Union,
    Unpack,
)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models.options import Options
from typesense import Client
from typesense import exceptions as typesense_exceptions
from typing_extensions import Literal

from typesense_integration.common.utils import ensure_is_subset_or_all, snake_case


class Field(TypedDict):
    """
    :py:class:`Field` represents the field types for a Typesense collection.

    :param parent: The parent field.
    :param child: The child field.
    :param non_relation_field: The non-relation field.

    """

    parent: NotRequired[models.ForeignKey[models.Model, models.Model]]
    child: NotRequired[models.ManyToOneRel]
    non_relation_field: NotRequired[models.Field[Any, Any]]


class FieldSet(TypedDict):
    """
    :py:class:`FieldSet` represents the set of field types for a Typesense collection.

    :param parents: The parent fields.
    :param childs: The child fields.
    :param non_relation_fields: The non-relation fields.

    """

    parents: NotRequired[set[models.ForeignKey[models.Model, models.Model]]]
    children: NotRequired[set[models.ManyToOneRel]]
    non_relation_fields: NotRequired[set[models.Field[Any, Any]]]


class Relation(TypedDict):
    """
    :py:class: `Relations` represents the relations for a Typesense collection.

    :param parent: The parent relation.
    :param child: The child relation.

    """

    parent: NotRequired[models.ForeignKey[models.Model, models.Model]]
    child: NotRequired[models.ManyToOneRel]


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
    default_sorting_field: NotRequired[SortableField | None]
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

SortableField = Union[
    models.IntegerField[Any, Any],
    models.FloatField[Any, Any],
    models.DecimalField[Any, Any],
    models.DateField[Any, Any],
    models.DateTimeField[Any, Any],
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
        models.DateField,
        models.DateTimeField,
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

        self.index_fields = kwargs.get('index_fields', set())
        self.skip_index_fields = kwargs.get('skip_index_fields', set())
        self.children = kwargs.get('children', set())
        self.parents = kwargs.get('parents', set())
        self.name = snake_case(
            self.utils.get_model_verbose_name_from_meta(self.model._meta),
        )
        self.non_relation_model_fields = self.utils.get_non_relation_fields_in_set(
            self.model._meta.get_fields(),
        )
        self.geopoints = kwargs.get('geopoints', set())
        self.use_joins = kwargs.get('use_joins', False)
        self.override_id = kwargs.get('override_id', False)
        self.non_relation_skipped_fields = self.utils.get_non_relation_fields_in_set(
            self.skip_index_fields,
        )

        self._handle_fields()

        self.default_sorting_field = self._handle_default_sorting_field(
            kwargs.get('default_sorting_field', None),
        )
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
        self.typesense_fields = self._handle_typesense_fields()
        self.typesense_relations = self._handle_typesense_relations()
        self.typesense_fields.extend(self._handle_typesense_geopoints())
    def _validate_client_and_model(self) -> None:
        if not isinstance(self.client, Client):
            raise typesense_exceptions.ConfigError(
                'Client must be an instance of Typesense Client.',
            )
        if not issubclass(self.model, models.Model):
            raise typesense_exceptions.ConfigError(
                'Model must be an instance of the default models.Model class.',
            )

    def _handle_default_sorting_field(
        self,
        field: SortableField | None,
    ) -> SortableField | None:
        """Handle the default sorting field."""
        if field is None:
            return None

        if field.name == 'id':
            raise typesense_exceptions.RequestMalformed(
                'Default sorting field cannot be the ID field.',
            )

        if (
            field not in self.non_relation_model_fields
            and field not in self.index_fields
        ):
            raise typesense_exceptions.RequestMalformed(
                'Default sorting field must be present schema.',
            )

        if field.__class__ not in self.mapped_sortable_types:
            raise typesense_exceptions.RequestMalformed(
                'Default sorting field must be of type Integer, Float or Decimal.',
            )

        return field

    def _handle_facets(self) -> None:
        """Handle facets."""
        if self.facets.intersection(self.parents) and not self.use_joins:
            warnings.warn(
                'Facetting on relation only affects JOINs',
                UserWarning,
                stacklevel=2,
            )

    def _handle_fields(self) -> None:
        if any([self.index_fields, self.parents, self.children, self.geopoints]):
            self._handle_explicit_fields()
            return

        if self.skip_index_fields:
            self._handle_mismatched_skips()

        fields = self._handle_implicit_fields()

        self.index_fields = fields.get('non_relation_fields', set())
        self.parents = fields.get('parents', set())
        self.children = fields.get('children', set())

    def _handle_explicit_fields(self) -> None:
        """Handle explicit fields."""
        self._handle_skipped_indexed_intersection()
        self._handle_geopoints_in_index_fields()
        self._handle_relations_in_index_fields()
        self._handle_mismatched_fields()
        self._handle_mismatched_skips()
        self._handle_multiple_of_same_field_name()
        self._handle_explicit_relations()
        self._handle_geopoints()

    def _handle_skipped_indexed_intersection(self) -> None:
        """Handle fields intersection."""
        intersection = self.index_fields.intersection(self.non_relation_skipped_fields)

        if intersection:
            raise typesense_exceptions.RequestMalformed(
                'Fields {fields} are present in both index and skip index fields.'.format(
                    fields=intersection,
                ),
            )

    def _handle_geopoints_in_index_fields(self) -> None:
        """Handle geopoints."""
        if self.utils.is_tuple_element_in_set(
            field_set=self.index_fields,
            tup_set=self.geopoints,
        ):
            raise typesense_exceptions.RequestMalformed(
                'Geopoints are already present in index fields.',
            )

    def _handle_relations_in_index_fields(self) -> None:
        """
        Handle relations in index fields.

        This shouldn't be possible, as relations are not allowed in index fields.
        But if untyped, it will be a set of Any, so we need to check.
        """
        relations = self.utils.get_relation_fields_in_set(self.index_fields)  # type: ignore[arg-type]
        if relations:
            raise typesense_exceptions.RequestMalformed(
                'Relations {relations} are not allowed in index fields.'.format(
                    relations=relations,
                ),
            )

    def _handle_geopoints(self) -> None:
        """Handle geopoints."""
        for lat, long in self.geopoints:
            lat_type = lat.__class__ in self.mapped_geopoint_types
            long_type = long.__class__ in self.mapped_geopoint_types

            if not lat_type:
                raise typesense_exceptions.RequestMalformed(
                    '\n'.join(
                        [
                            f'Geopoint {lat_type} is not supported. Supported types:',
                            f'{self.mapped_geopoint_types}',
                        ],
                    ),
                )

            if not long_type:
                raise typesense_exceptions.RequestMalformed(
                    '\n'.join(
                        [
                            f'Geopoint {long_type} is not supported. Supported types:',
                            f'{self.mapped_geopoint_types}',
                        ],
                    ),
                )

    def _handle_explicit_relations(self) -> None:
        """Handle explicit references."""
        mismatched_parents, mismatched_children = self.utils.get_mismatched_relations(
            children=self.children,
            parents=self.parents,
            model=self.model,
        )

        if mismatched_parents:
            raise typesense_exceptions.RequestMalformed(
                'Model {model} has no foreign relations {relations}.'.format(
                    model=self.model._meta.model,
                    relations=mismatched_parents,
                ),
            )

        if mismatched_children:
            raise typesense_exceptions.RequestMalformed(
                'Model {model} has no foreign relations {relations}.'.format(
                    model=self.model._meta.model,
                    relations=mismatched_children,
                ),
            )

    def _handle_multiple_of_same_field_name(self) -> None:
        """Handle multiple of the same field name."""
        if self.utils.has_multiple_of_same_field_name(self.index_fields):
            raise typesense_exceptions.RequestMalformed('Field names must be unique.')

    def _handle_mismatched_skips(self) -> None:
        """Handle mismatched skips."""
        mismatched_skips = self.skip_index_fields - self.non_relation_model_fields

        if mismatched_skips:
            warnings.warn(
                f'Some fields: {mismatched_skips} are not present in the model.',
                UserWarning,
                stacklevel=2,
            )

    def _handle_mismatched_fields(self) -> None:
        """Handle mismatched fields."""
        mismatched_fields = self.index_fields - self.non_relation_model_fields

        if mismatched_fields:
            warnings.warn(
                f'Some fields: {mismatched_fields} are not present in the model.',
                UserWarning,
                stacklevel=2,
            )

    def _handle_implicit_fields(self) -> FieldSet:
        non_relation_fields: set[models.Field[Any, Any]] = set()

        parents: set[models.ForeignKey[models.Model, models.Model]] = set()
        children: set[models.ManyToOneRel] = set()

        for field in self.model._meta.get_fields():
            processed_field = self.utils.process_field(
                field=field,
                index_fields=self.index_fields,
                skip_index_fields=self.skip_index_fields,
                override_id=self.override_id,
                model=self.model,
            )

            if processed_field.get('child'):
                children.add(processed_field['child'])

            if processed_field.get('parent'):
                parents.add(processed_field['parent'])

            if processed_field.get('non_relation_field'):
                non_relation_fields.add(processed_field['non_relation_field'])

        return {
            'non_relation_fields': non_relation_fields,
            'parents': parents,
            'children': children,
        }

    def _handle_typesense_fields(self) -> list[APIField]:
        """Handle Typesense fields."""
        non_relations_skip_index_fields = self.utils.get_non_relation_fields_in_set(
            self.skip_index_fields,
        )

        return [
            {
                'type': TypesenseCollectionUtils.handle_typesense_field_type(
                    self.mapped_field_types,
                    field,
                ),
                'name': field.name,
                'facet': field in self.facets,
                'index': self.utils.is_field_indexed(
                    field=field,
                    skip_index_fields=self.skip_index_fields,
                    index_fields=self.index_fields,
                ),
                # 'optional': field.blank or field.null,
            }
            for field in (self.index_fields | non_relations_skip_index_fields)
        ]

    def _handle_typesense_geopoints(self) -> list[APIField]:
        """Handle Typesense geopoints."""
        return [
            {
                'name': f'{long}_{lat}',
                'type': 'geopoint',
                'facet': lat in self.facets or long in self.facets,
                'index': self.utils.is_field_indexed(
                    lat,
                    index_fields=self.index_fields,
                    skip_index_fields=self.skip_index_fields,
                )
                or self.utils.is_field_indexed(
                    long,
                    index_fields=self.index_fields,
                    skip_index_fields=self.skip_index_fields,
                ),
            }
            for long, lat in self.geopoints
        ]

    def _handle_typesense_relations(self) -> list[APIField]:
        """Handle Typesense relations."""
        typesense_relations: list[APIField] = []

        if self.use_joins:
            for field in self.parents:
                typesense_relations.append(
                    self.utils.join_on_field(
                        field=field,
                        facets=self.facets,
                        model=self.model,
                        skip_index_fields=self.skip_index_fields,
                        valid_types=self.mapped_field_types,
                    ),
                )

        for reference in self.detailed_parents:
            typesense_relations.append(
                {
                    'name': reference.name,
                    'type': 'object',
                    'index': reference not in self.skip_index_fields,
                    'facet': False,
                },
            )

        for child in self.detailed_children:
            typesense_relations.append(
                {
                    'name': child.name,
                    'type': 'object[]',
                    'index': child not in self.skip_index_fields,
                    'facet': False,
                },
            )

        return typesense_relations


_TField = TypeVar('_TField', bound=models.Field[Any, Any])


class TypesenseCollectionUtils:
    """Utility functions for Typesense collections."""

    @staticmethod
    def handle_composite_foreign_key(
        field: models.ForeignKey[models.Model, models.Model],
    ) -> None:
        """Handle composite foreign keys."""
        if TypesenseCollectionUtils.is_composite_foreign_key(field):
            raise typesense_exceptions.RequestMalformed(
                f'Composite key {field} is not allowed',
            )

    @staticmethod
    def raise_on_self_reference(
        model: type[models.Model],
        field: models.ForeignKey[models.Model, models.Model] | models.ForeignObjectRel,
    ) -> None:
        """
        Raise an exception if a field is a self reference.

        :param model: The model to check.
        :param field: The field to check.

        :raises Typesense.Exceptions.RequestMalformed: If the field is a self reference.
        """
        if TypesenseCollectionUtils.is_self_reference(model, field):
            raise typesense_exceptions.RequestMalformed(
                'Self reference is not allowed.',
            )

    @staticmethod
    def is_self_reference(
        model: type[models.Model],
        field: models.ForeignKey[models.Model, models.Model] | models.ForeignObjectRel,
    ) -> bool:
        """
        Check if a field is a self reference.

        :param model: The model to check.
        :param field: The field to check.

        :return: True if the field is a self reference, False otherwise.

        """
        return field.related_model == model

    @staticmethod
    def get_related_model_meta(
        field: models.ForeignKey[models.Model, models.Model],
    ) -> Options[models.Model]:
        """
        Get the meta class of the related model.

        :param field: The field to get the related model meta class from.

        :return: The meta class of the related model.

        :raises Typesense.Exceptions.RequestMalformed: If the related model has no meta class.

        """
        if (
            isinstance(field.related_model, str)
            or getattr(field.related_model, '_meta', None) is None
        ):
            raise typesense_exceptions.RequestMalformed(
                'Invalid or missing meta class on related model',
            )

        return field.related_model._meta

    @staticmethod
    def is_composite_foreign_key(
        field: models.ForeignKey[models.Model, models.Model],
    ) -> bool:
        """
        Determine if a foreign key is composite.

        :param field: The field to check.

        :return: True if the foreign key is composite, False otherwise.

        """
        return len(field.related_fields) > 1

    @staticmethod
    def handle_decimal_field(
        field: models.DecimalField[Any, Any],
    ) -> str:
        """
        Determines the appropriate Typesense field type for a `DecimalField` based
         on its size and precision.

        `float32` can represent values up to `~3.4E+38`, but precision might be lost for
        values larger than `1E+7`, while
        `float64` can represent values up to `~1.7E+308`, with precision up to 15-17
        decimal digits


        :param field: The `DecimalField` to handle.


        :return: The Typesense field type (`float32` or `float64`) for the `DecimalField`.
        """
        max_float_value = 3.4e38
        max_field_value = (10 ** (field.max_digits - field.decimal_places)) - (
            10**-field.decimal_places
        )

        if max_field_value < max_float_value and field.decimal_places <= 7:
            return 'float32'

        return 'float64'

    @staticmethod
    def join_on_field(
        *,
        model: type[models.Model],
        skip_index_fields: set[models.Field[Any, Any] | models.ForeignObjectRel],
        facets: set[
            models.Field[Any, Any] | models.ForeignKey[models.Model, models.Model]
        ],
        field: models.ForeignKey[models.Model, models.Model],
        valid_types: dict[type[models.Field[Any, Any]], str],
    ) -> APIField:
        """
        Create a Typesense field for a foreign key.

        :param model: The model to create the field for.
        :param skip_index_fields: The fields to skip indexing.

        :return: The Typesense field for the foreign key.

        :raises Typesense.Exceptions.RequestMalformed: If the related model has no verbose name.
        """
        TypesenseCollectionUtils.handle_composite_foreign_key(field)
        TypesenseCollectionUtils.raise_on_self_reference(model, field)

        _, related_field = field.related_fields[0]

        related_model_meta = TypesenseCollectionUtils.get_related_model_meta(field)

        if not isinstance(related_model_meta.verbose_name, str):
            raise typesense_exceptions.RequestMalformed(
                f'Model {related_model_meta} has no verbose name.',
            )

        related_model_name = TypesenseCollectionUtils.get_model_verbose_name_from_meta(
            related_model_meta,
        )

        related_model_name_snake_case = snake_case(related_model_name)

        return {
            'name': f'{field.name}_{related_field.name}',
            'type': TypesenseCollectionUtils.handle_typesense_field_type(
                valid_types,
                related_field,
            ),
            'reference': f'{related_model_name_snake_case}.{related_field.name}',
            'index': field not in skip_index_fields,
            'facet': field in facets,
        }

    @staticmethod
    def get_model_verbose_name_from_meta(meta: Options[models.Model]) -> str:
        """
        Get the verbose name of a model.

        :param model: The model to get the verbose name from.

        :return: The verbose name of the model.

        :raises Typesense.Exceptions.RequestMalformed: If the model has no verbose name.
        """
        if not isinstance(meta.verbose_name, str):
            raise typesense_exceptions.RequestMalformed(
                f'Model {meta} has no verbose name.',
            )

        return meta.verbose_name

    @staticmethod
    def handle_typesense_field_type(
        valid_types: dict[type[models.Field[Any, Any]], str],
        field: models.Field[Any, Any],
    ) -> str:
        """
        Handle Typesense field type.

        :param field: The field to handle.
        :param valid_types: The valid field types.

        :return: The Typesense field type for the field.

        :raises Typesense.Exceptions.RequestMalformed: If the field type is not supported.
        """
        if field.name == 'id':
            return 'string'

        typesense_type = valid_types.get(field.__class__)
        if not typesense_type:
            raise typesense_exceptions.RequestMalformed(
                'Field type for {field} is not supported. Supported types: \n {types}'.format(
                    field=field,
                    types=valid_types.keys(),
                ),
            )

        if isinstance(field, models.DecimalField):
            return TypesenseCollectionUtils.handle_decimal_field(field)

        return typesense_type

    @staticmethod
    def should_skip_field(
        field: models.Field[Any, Any] | models.ForeignObjectRel,
        override_id: bool,
    ) -> bool:
        """
        Checks if a field should be skipped.

        If the field is the ID field and the caller does not want to override the default
        ID field, the field should be skipped.

        :param field: The field to check.
        :param override_id: Whether to override the default ID field.

        :return: True if the field should be skipped, False otherwise.

        """
        return field.name == 'id' and not override_id

    @staticmethod
    def get_relation_fields_in_set(
        fields: set[models.Field[Any, Any] | models.ForeignObjectRel],
    ) -> set[models.Field[Any, Any] | models.ForeignObjectRel]:
        """
        Get the relation fields in a set.

        :param fields: The set of fields to check.

        :return: The relation fields in the set.

        """
        return {field for field in fields if field.is_relation}

    @staticmethod
    def get_non_relation_fields_in_set(
        fields: Iterable[
            models.Field[Any, Any] | models.ForeignObjectRel | GenericForeignKey
        ],
    ) -> set[models.Field[Any, Any]]:
        """
        Get the non-relation fields in a set.

        :param fields: The set of fields to check.

        :return: The non-relation fields in the set.

        """
        return {
            field
            for field in fields
            if TypesenseCollectionUtils.is_non_relation_field(field)
        }

    @staticmethod
    def is_non_relation_field(
        field: models.Field[Any, Any] | models.ForeignObjectRel | GenericForeignKey,
    ) -> TypeGuard[models.Field[Any, Any]]:
        """
        Check if a field is a valid field for indexing.

        :param field: The field to check.

        :return: True if the field is a valid field for indexing, False otherwise.
        """
        return isinstance(field, models.Field) and not field.is_relation

    @staticmethod
    def is_field_indexed(
        field: models.Field[Any, Any] | models.ForeignObjectRel,
        skip_index_fields: set[models.Field[Any, Any] | models.ForeignObjectRel],
        index_fields: set[models.Field[Any, Any]],
    ) -> bool:
        """
        Check if a field is indexed.

        Since the index fields are non-relations, and relations can be skipped, there
        needs to be two checks: one for the field not being in the skip index fields, and
        one for the field being in the index fields.

        :param field: The field to check.

        :return: True if the field is indexed, False otherwise.
        """
        return field not in skip_index_fields or field in index_fields

    @staticmethod
    def get_mismatched_relations(
        model: type[models.Model],
        parents: set[models.ForeignKey[models.Model, models.Model]],
        children: set[models.ManyToOneRel],
    ) -> Tuple[
        set[models.ForeignKey[models.Model, models.Model]],
        set[models.ManyToOneRel],
    ]:
        """
        Get the mismatched relations for a model.

        :param model: The model to check.
        :param parents: The parent relations to check.
        :param children: The child relations to check.

        :return: A tuple containing the mismatched parent relations and the mismatched
            child relations.
        """
        model_references: set[models.ForeignKey[models.Model, models.Model]] = set()
        model_referenced_by: set[models.ManyToOneRel] = set()

        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey) and field.many_to_one:
                model_references.add(field)
            if isinstance(field, models.ManyToOneRel) and field.one_to_many:
                model_referenced_by.add(field)

        mismatched_parents = parents - model_references
        mismatched_children = children - model_referenced_by

        return mismatched_parents, mismatched_children

    @staticmethod
    def has_multiple_of_same_field_name(field_set: set[models.Field[Any, Any]]) -> bool:
        """
        Check if a set has multiple fields with the same name.

        :param field_set: The set to check.

        :return: True if the set has multiple fields with the same name, False otherwise.
        """
        seen = set()

        for field in field_set:
            if field.name in seen:
                return True
            seen.add(field.name)

        return False

    @staticmethod
    def is_tuple_element_in_set(
        field_set: set[models.Field[Any, Any]],
        tup_set: set[Tuple[_TField, _TField]],
    ) -> bool:
        """
        Check if a set of tuples has any of its elements in a set.

        :param field_set: The set to check against.
        :param tup_set: The set of tuples to check.

        :return: True if any of the elements in the set of tuples are in the set, False
            otherwise.

        """
        return any(lat in field_set or long in field_set for lat, long in tup_set)

    @staticmethod
    def get_mismatched_fields_in_sets(
        original_set: set[models.Field[Any, Any]],
        other_set: set[models.Field[Any, Any]],
    ) -> set[models.Field[Any, Any]]:
        """
        Get the mismatched fields in two sets.

        :param original_set: The original set.
        :param other_set: The other set.

        :return: The mismatched fields in the two sets.

        """
        return original_set - other_set

    @staticmethod
    def process_field(
        *,
        field: models.Field[Any, Any] | models.ForeignObjectRel | GenericForeignKey,
        index_fields: set[models.Field[Any, Any]],
        skip_index_fields: set[models.Field[Any, Any] | models.ForeignObjectRel],
        override_id: bool,
        model: type[models.Model],
    ) -> Field:
        """
        Process a field.

        If the field is a generic foreign key, raise an exception. If the field is a
        non-relation field and indexed, return a dictionary with the non-relation field.
        If the field is a relation field, return a dictionary with the parent or child
        field.

        :param field: The field to process.
        :param index_fields: The set of fields to be indexed.
        :param skip_index_fields: The set of fields to not be indexed.
        :param override_id: Whether to override the default ID field.
        :param model: The model to check.

        :return: A dictionary with the parent or child field, or an empty dictionary.

        """
        if isinstance(field, GenericForeignKey):
            raise typesense_exceptions.RequestMalformed(
                'Generic foreign keys are not allowed.',
            )

        if TypesenseCollectionUtils.should_skip_field(
            field=field,
            override_id=override_id,
        ):
            return {}

        if TypesenseCollectionUtils.is_non_relation_field(
            field,
        ) and TypesenseCollectionUtils.is_field_indexed(
            field=field,
            index_fields=index_fields,
            skip_index_fields=skip_index_fields,
        ):
            return {'non_relation_field': field}

        return TypesenseCollectionUtils.process_relation_field(field, model)

    @staticmethod
    def process_relation_field(
        field: models.Field[Any, Any] | models.ForeignObjectRel,
        model: type[models.Model],
    ) -> Field:
        """
        Process a relation field. If the field is a self reference, raise an exception.

        If the field is a many to many field, raise an exception. If the field is a
        many to one field, return a dictionary with the parent field. If the field is a
        one to many field, return a dictionary with the child field.

        :param field: The field to process.
        :param model: The model to check.

        :return: A dictionary with the parent or child field, or an empty dictionary.

        :raises Typesense.Exceptions.RequestMalformed: If the field is a self reference or
            many to many field.

        """
        if isinstance(field, (models.ForeignKey, models.ForeignObjectRel)):
            TypesenseCollectionUtils.raise_on_self_reference(model=model, field=field)

        if field.many_to_many:
            raise typesense_exceptions.RequestMalformed(
                'Implicit Many to many field {field} is not allowed.'.format(
                    field=field,
                ),
            )

        if isinstance(field, models.ForeignKey) and field.many_to_one:
            return {'parent': field}

        elif isinstance(field, models.ManyToOneRel) and field.one_to_many:
            return {'child': field}

        return {}
