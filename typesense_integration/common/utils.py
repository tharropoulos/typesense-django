"""Utility functions for Typesense integration."""

import re


def snake_case(string: str) -> str:
    """Convert a string to snake_case."""
    string = string.lower().replace('-', ' ').replace('.', ' ')

    # Apply regular expression substitutions for title case conversion
    # and add an underscore between words
    return '_'.join(
        re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split(),
    )
