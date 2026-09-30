"""config.py — Validate the file_size section of ~/.tingle/code_check/config.json.

The file is read by the generic `code_check.config.load_sections`; `SCHEMA`
and `validate` hold the rules for the `file_size` section (the deprecated
`check_file_size` section follows the same rules).
`ConfigError` is re-exported from `code_check.config`.

Dependencies: standard library only.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from code_check.config import ConfigError

__all__ = ["SCHEMA", "ConfigError", "Validator", "validate"]

# A validator returns None when `value` is valid, else the reason it is not.
Validator = Callable[[str, Any], "str | None"]


def _non_negative_int(key: str, value: Any) -> str | None:
    """Accept an int >= 0; JSON booleans are rejected (bool subclasses int)."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return f"'{key}' must be an integer >= 0"
    return None


def _list_of_str(key: str, value: Any) -> str | None:
    """Accept a list whose items are all strings (an empty list is fine)."""
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        return f"'{key}' must be a list of strings"
    return None


def _boolean(key: str, value: Any) -> str | None:
    """Accept `true` or `false`."""
    if not isinstance(value, bool):
        return f"'{key}' must be a boolean"
    return None


def _one_of(choices: list[str], nullable: bool = False) -> Validator:
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


# file_size section: key → validator.
SCHEMA: dict[str, Validator] = {
    "warn": _non_negative_int,
    "error": _non_negative_int,
    "critical": _non_negative_int,
    "top": _non_negative_int,
    "exclude": _list_of_str,
    "ignore": _list_of_str,
    "include": _list_of_str,
    "ext": _list_of_str,
    "no_default_excludes": _boolean,
    "gitignore": _boolean,
    "fail_on": _one_of(["warn", "error", "critical"], nullable=True),
    "min_level": _one_of(["ok", "warn", "error", "critical"]),
}


def validate(section: dict, path: Path) -> dict:
    """Check a `file_size` section against `SCHEMA` and return it unchanged.

    Raises `ConfigError(path, ...)` for an unknown key or a bad value.
    """
    for key, value in section.items():
        validator = SCHEMA.get(key)
        if validator is None:
            raise ConfigError(path, f"unknown key '{key}'")
        reason = validator(key, value)
        if reason is not None:
            raise ConfigError(path, reason)
    return section
