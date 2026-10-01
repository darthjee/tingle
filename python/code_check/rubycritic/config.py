"""config.py — Validate the rubycritic section of ~/.tingle/code_check/config.json.

The file is read by the generic `code_check.config.load_section`; `SCHEMA`
and `validate` hold the rules for the `rubycritic` section. The validators
come from `code_check.validators`. There is no `ext` key: rubycritic always
analyses Ruby files, so `ext` is reported as an unknown key. The thresholds
are not compared with each other.
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
    non_empty_str,
    non_negative_int,
    non_negative_number,
    nullable_non_negative_int,
    one_of,
    validate_section,
)

__all__ = ["SCHEMA", "ConfigError", "validate"]

# rubycritic section: key → validator.
SCHEMA: dict[str, Validator] = {
    "warn": non_negative_number,
    "error": non_negative_number,
    "critical": non_negative_number,
    "top": non_negative_int,
    "exclude": list_of_str,
    "ignore": list_of_str,
    "include": list_of_str,
    "no_default_excludes": boolean,
    "gitignore": boolean,
    "fail_on": one_of(["warn", "error", "critical"], nullable=True),
    "min_level": one_of(["ok", "warn", "error", "critical"]),
    "image": non_empty_str,
    "details": nullable_non_negative_int,
}


def validate(section: dict, path: Path) -> dict:
    """Check a `rubycritic` section against `SCHEMA` and return it unchanged.

    Keys are checked in the section's order. Raises `ConfigError(path, ...)`
    for the first unknown key (`ext` included) or bad value.
    """
    return validate_section(section, SCHEMA, path)
