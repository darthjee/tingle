"""validators.py — Generic value validators for code_check config sections.

Each validator takes `(key, value)` and returns None when the value is valid,
or a human-readable reason when it is not. `validate_section` checks a whole
section against a `{key: validator}` schema. The subcommand `config.py`
modules (`file_size`, `rubycritic`) build their schemas from these.

Dependencies: standard library only.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from pathlib import Path
from typing import Any

from code_check.config import ConfigError

__all__ = [
    "Validator",
    "boolean",
    "list_of_str",
    "non_empty_str",
    "non_negative_int",
    "non_negative_number",
    "nullable_non_negative_int",
    "one_of",
    "validate_section",
]

# A validator returns None when `value` is valid, else the reason it is not.
Validator = Callable[[str, Any], "str | None"]


def _is_non_negative_int(value: Any) -> bool:
    """Return True for an int >= 0 that is not a bool (bool subclasses int)."""
    return not isinstance(value, bool) and isinstance(value, int) and value >= 0


def non_negative_int(key: str, value: Any) -> str | None:
    """Accept an int >= 0; JSON booleans are rejected (bool subclasses int)."""
    if not _is_non_negative_int(value):
        return f"'{key}' must be an integer >= 0"
    return None


def nullable_non_negative_int(key: str, value: Any) -> str | None:
    """Accept `null` or an int >= 0; booleans and floats are rejected."""
    if value is not None and not _is_non_negative_int(value):
        return f"'{key}' must be an integer >= 0 or null"
    return None


def non_negative_number(key: str, value: Any) -> str | None:
    """Accept a finite int or float >= 0; booleans, NaN and Infinity are rejected."""
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        return f"'{key}' must be a number >= 0"
    return None


def non_empty_str(key: str, value: Any) -> str | None:
    """Accept a string that is not empty after trimming whitespace."""
    if not isinstance(value, str) or not value.strip():
        return f"'{key}' must be a non-empty string"
    return None


def list_of_str(key: str, value: Any) -> str | None:
    """Accept a list whose items are all strings (an empty list is fine)."""
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        return f"'{key}' must be a list of strings"
    return None


def boolean(key: str, value: Any) -> str | None:
    """Accept `true` or `false`."""
    if not isinstance(value, bool):
        return f"'{key}' must be a boolean"
    return None


def one_of(choices: list[str], nullable: bool = False) -> Validator:
    """Build a validator accepting one of `choices` (and `null` when `nullable`)."""
    names = [*choices, "null"] if nullable else list(choices)
    described = f"{', '.join(names[:-1])} or {names[-1]}"

    def check(key: str, value: Any) -> str | None:
        if value is None and nullable:
            return None
        if not isinstance(value, str) or value not in choices:
            return f"'{key}' must be one of {described}"
        return None

    return check


def validate_section(section: dict, schema: dict[str, Validator], path: Path) -> dict:
    """Check `section` against `schema` and return it unchanged.

    Keys are checked in the section's order. Raises `ConfigError(path, ...)`
    for the first unknown key or bad value.
    """
    for key, value in section.items():
        validator = schema.get(key)
        if validator is None:
            raise ConfigError(path, f"unknown key '{key}'")
        reason = validator(key, value)
        if reason is not None:
            raise ConfigError(path, reason)
    return section
