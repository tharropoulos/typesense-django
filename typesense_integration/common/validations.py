import pdb
from typing import Any, Iterable, Optional, TypeGuard, TypeVar

from attr import validate
from django.db import models

from typesense_integration.common.utils import snake_case
from typesense_integration.types import TypesenseField

TField = TypeVar('TField')
TModel = TypeVar('TModel')
TSet = TypeVar('TSet')
TType = TypeVar('TType')


def validate_instance(instance: TField, model: type[TField]) -> TypeGuard[TField]:
    """
    Validate that the instance is an instance of the model.

    :param instance: The instance to validate.
    :param model: The model to validate against.

    :return: True if the instance is an instance of the model.

    """
    return isinstance(instance, model) or issubclass(type(instance), model)


def handle_name(model: models.Model, name: Optional[str] = None) -> str:
    """
    Handle the name of the model.

    :param model: The model.
    :param name: The explicit name

    :return The name of the model if there's no explicit name, otherwise the explicit name.

    :raises ValueError: If the model is not a subclass of django.db.models.Model.

    """
    if name:
        return name

    if not validate_instance(model, models.Model):
        raise ValueError('Model must be a subclass of django.db.models.Model')

    if not isinstance(model._meta.verbose_name, str):
        raise ValueError('Verbose name must be a string')

    return snake_case(model._meta.verbose_name)


def handle_explicit_field(
    typesense_field: TypesenseField[TField, TType],
    valid_types: set[TSet],
) -> TypesenseField[TField, TType]:
    if not is_field_type_valid(
        type_=typesense_field.get('type'), valid_types=valid_types
    ):
        raise ValueError('Field type is not supported')

    return typesense_field


def is_field_type_valid(
    valid_types: set[TSet],
    type_: Optional[TType] = None,
) -> TypeGuard[TSet]:
    return type_ in valid_types


def handle_field(
    field: TypesenseField[TField, TType],
    model_fields: set[TModel],
) -> TypesenseField[TField, TType]:
    associated_model_field = field.get('associated_model_field')

    if not associated_model_field:
        raise ValueError('Field name and associated model field are required')

    if isinstance(associated_model_field, Iterable):
        validate_field_in_model(associated_model_field, model_fields)
    else:
        validate_field_in_model(
            fields=(associated_model_field,), model_fields=model_fields
        )

    return field


def validate_field_in_model(
    fields: Iterable[TField],
    model_fields: set[TModel],
) -> None:
    if not all(fields):
        raise ValueError('Both associated model fields are required')

    for field in fields:
        if field not in model_fields:
            raise ValueError('Field does not exist in the model')

    if not all(field in model_fields for field in fields):
        raise ValueError('Field does not exist in the model')
