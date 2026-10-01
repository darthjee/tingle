"""config.py — Validate the file_size section of ~/.tingle/code_check/config.json.

The file is read by the generic `code_check.config.load_sections`; `SCHEMA`
and `validate` hold the rules for the `file_size` section (the deprecated
`check_file_size` section follows the same rules). The validators come from
`code_check.validators`.
`ConfigError` is re-exported from `code_check.config`.

Dependencies: standard library only.
"""

from __future__ import annotations

from pathlib import Path

from code_check.config import ConfigError
from code_check.validators import (
    Validator,
    boolean,
    list_of_str,
    non_negative_int,
    one_of,
    validate_section,
)

__all__ = ["SCHEMA", "ConfigError", "Validator", "validate"]

# file_size section: key → validator.
SCHEMA: dict[str, Validator] = {
    "warn": non_negative_int,
    "error": non_negative_int,
    "critical": non_negative_int,
    "top": non_negative_int,
    "exclude": list_of_str,
    "ignore": list_of_str,
    "include": list_of_str,
    "ext": list_of_str,
    "no_default_excludes": boolean,
    "gitignore": boolean,
    "fail_on": one_of(["warn", "error", "critical"], nullable=True),
    "min_level": one_of(["ok", "warn", "error", "critical"]),
}


def validate(section: dict, path: Path) -> dict:
    """Check a `file_size` section against `SCHEMA` and return it unchanged.

    Raises `ConfigError(path, ...)` for an unknown key or a bad value.
    """
    return validate_section(section, SCHEMA, path)
