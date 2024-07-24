from typing import (
    Any,
    Generic,
    Literal,
    NotRequired,
    Tuple,
    TypedDict,
    TypeGuard,
    TypeVar,
)

from django.db import models

TModelField = TypeVar('TModelField')
TType = TypeVar('TType')

FieldTypes = Literal[
    'string',
    'string[]',
    'int32',
    'int32[]',
    'int64',
    'int64[]',
    'float',
    'float[]',
    'bool',
    'bool[]',
    'object',
    'object[]',
    'string*',
    'image',
    'auto',
]

Geopoint = Tuple[
    models.FloatField[Any, Any] | models.DecimalField[Any, Any],
    models.FloatField[Any, Any] | models.DecimalField[Any, Any],
]

ReferenceFieldTypes = Literal['string', 'int32', 'int64', 'float']

GeopointFieldTypes = Literal['geopoint']


Locales = Literal['ja', 'zh', 'ko', 'th', 'el', 'ru', 'rs', 'uk', 'be']


class TypesenseField(Generic[TModelField, TType], TypedDict):
    """"""

    name: NotRequired[str]
    facet: NotRequired[bool]
    optional: NotRequired[bool]
    infix: NotRequired[bool]
    stem: NotRequired[bool]
    locale: NotRequired[Locales]
    sort: NotRequired[bool]
    store: NotRequired[bool]
    num_dim: NotRequired[float]
    range_index: NotRequired[str]
    vec_dist: NotRequired[Literal['cosine', 'ip']]
    associated_model_field: TModelField
    type: NotRequired[TType]


class RegularField(TypesenseField[models.Field[Any, Any], FieldTypes]):
    """"""


class ReferenceField(
    TypesenseField[models.ForeignKey[models.Model, models.Model], ReferenceFieldTypes],
):
    """"""

    reference: NotRequired[str]


class GeopointField(TypesenseField[Geopoint, GeopointFieldTypes]):
    """"""
