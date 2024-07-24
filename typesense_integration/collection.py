from __future__ import annotations

import pdb
from typing import Any, ClassVar, TypedDict, TypeGuard, Union, Unpack, cast, get_args

from django.db import models
from typesense import Client

from typesense_integration.common.utils import snake_case
from typesense_integration.common.validations import validate_instance
from typesense_integration.types import (
    FieldTypes,
    Geopoint,
    GeopointField,
    ReferenceField,
    RegularField,
)


class CollectionParams(TypedDict):

    fields: list[Union[RegularField, ReferenceField, GeopointField]]
    name: str
    default_sorting_field: str
    token_separators: list[str]
    symbols_to_index: list[str]
    model: type[models.Model]
    client: Client


class Collection:
    mapped_valid_types: set[FieldTypes] = set(get_args(FieldTypes))

    mapped_field_types: ClassVar[dict[type[models.Field[Any, Any]], FieldTypes]] = {
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
        models.BooleanField: 'bool',
        models.DateField: 'int64',
        models.DateTimeField: 'int64',
        models.DecimalField: 'float',
        models.FloatField: 'float',
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
        self.fields = kwargs.get('fields', [])
        self.default_sorting_field = kwargs.get('default_sorting_field', '')
        self.token_separators = kwargs.get('token_separators', [])
        self.symbols_to_index = kwargs.get('symbols_to_index', [])
        self.client = kwargs.get('client')
        self.model = kwargs['model']
        self.name = self._handle_name(kwargs.get('name'))

        self._validate_client()
        self._validate_model()

        self.model_fields = set(self.model._meta.get_fields())

        self.typesense_fields = []
        for field in self.fields:
            self.typesense_fields.append(self._handle_field(field))

    def _handle_name(self, name: str | None) -> str:
        if not name:
            if not isinstance(self.model._meta.verbose_name, str):
                raise ValueError('Model verbose name must be a string')

            return snake_case(self.model._meta.verbose_name)

        return name

    def _validate_client(self) -> None:
        if not validate_instance(self.client, Client):
            raise ValueError('Client must be an instance of typesense.Client')

    def _validate_model(self) -> None:
        if not self.model:
            raise ValueError('Model is required')

        if not validate_instance(self.model, models.Model):
            raise ValueError('Model must be a subclass of django.db.models.Model')

    def _validate_field(
        self,
        field: TypesenseField,
    ) -> Union[
        models.Field[Any, Any],
        models.ForeignKey[models.Model, models.Model],
        Geopoint,
    ]:
        associated_model_field = field.get('associated_model_field')

        if not associated_model_field:
            raise ValueError('Field name and associated model field are required')

        if isinstance(associated_model_field, models.Field):
            self._validate_regular_field(associated_model_field)

        if isinstance(associated_model_field, models.ForeignKey):
            self._validate_regular_field(associated_model_field)

        if isinstance(associated_model_field, tuple):
            self._validate_geopoint_field(associated_model_field)

        return associated_model_field

    def _is_field_type_valid(self, type_: str | None) -> TypeGuard[FieldTypes]:
        return type_ in self.mapped_valid_types

    def _validate_regular_field(
        self,
        regular_field: (
            models.Field[Any, Any] | models.ForeignKey[models.Model, models.Model]
        ),
    ) -> None:
        if all(
            regular_field not in self.model_fields for regular_field in regular_field
        ):
            raise ValueError('Field does not exist in the model')

    def _validate_geopoint_field(
        self,
        geopoint: Geopoint,
    ) -> None:
        if not all(geopoint):
            raise ValueError('Both associated model fields are required')

        if not all(field in self.model_fields for field in geopoint):
            raise ValueError('Field does not exist in the model')

    def _handle_field(
        self,
        field: Union[RegularField, ReferenceField, GeopointField],
    ) -> Union[RegularField, ReferenceField, GeopointField]:
        associated_model_field = self._validate_field(field)

        if not all([field.get('name'), field.get('type')]):
            if not isinstance(associated_model_field, models.Field):
                raise ValueError(
                    'Cannot set either reference or geopoint field type implicitly',
                )

            return self._handle_implicit_field(cast(RegularField, field))

        if bool(field.get('name')) != bool(field.get('type')):
            raise ValueError('Both field name and type are required')

        return self._handle_explicit_field(field)

    def _handle_explicit_field(
        self,
        typesense_field: Union[RegularField, ReferenceField, GeopointField],
    ) -> Union[RegularField, ReferenceField, GeopointField]:
        if not self._is_field_type_valid(typesense_field.get('type')):
            raise ValueError('Field type is not supported')

        return typesense_field

    def _handle_implicit_field(
        self,
        typesense_field: RegularField,
    ) -> RegularField:
        associated_model_field = typesense_field.get('associated_model_field')

        if not associated_model_field:
            raise ValueError('Field is required')

        typesense_field['name'] = snake_case(associated_model_field.name)
        typesense_field['type'] = self._map_typesense_type(associated_model_field)

        return typesense_field

    def _map_typesense_type(self, model_field: models.Field[Any, Any]) -> FieldTypes:
        typesense_type = self.mapped_field_types.get(model_field.__class__)

        if not typesense_type:
            raise ValueError(f'Field type {model_field.__class__} is not supported')

        return typesense_type
