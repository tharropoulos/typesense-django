"""Utility functions for Typesense integration."""

import re
from typing import TypeVar

from typesense import exceptions as typesense_exceptions
from typing_extensions import Literal


def snake_case(string: str) -> str:
    """Convert a string to snake_case."""
    string = string.lower().replace('-', ' ').replace('.', ' ')

    # Apply regular expression substitutions for title case conversion
    # and add an underscore between words
    return '_'.join(
        re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split(),
    )


_TSet = TypeVar('_TSet')


def ensure_is_subset_or_all(
    input_set: set[_TSet] | Literal[True],
    final_set: set[_TSet],
) -> set[_TSet]:
    """
    Ensure that the input set is a subset of the final set or if true, the final set.

    :param input_set: The input set to check.
    :param final_set: The final set to check against.

    :return: The input set if it is a subset of the final set.

    :raises typesense_exceptions.RequestMalformed: If the input set is not a subset
     of the final set.

    """
    if input_set is True:
        return final_set

    if not input_set.issubset(final_set):
        raise typesense_exceptions.RequestMalformed(
            f'{input_set} must be a subset of {final_set}',
        )

    return input_set
