"""config.py — Validate the php_complexity section of ~/.tingle/code_check/config.json.

A stub until the config section lands (#350): `SCHEMA` is empty, so
`validate` reports any key as unknown. The executor does not read the config
file yet. `ConfigError` is re-exported from `code_check.config`.

Dependencies: standard library only.
"""

from __future__ import annotations

from pathlib import Path

from code_check.config import ConfigError
from code_check.validators import Validator, validate_section

__all__ = ["SCHEMA", "ConfigError", "validate"]

# php_complexity section: key → validator (empty until #350).
SCHEMA: dict[str, Validator] = {}


def validate(section: dict, path: Path) -> dict:
    """Check a `php_complexity` section against `SCHEMA` and return it unchanged.

    Raises `ConfigError(path, ...)` for the first key (every key is unknown).
    """
    return validate_section(section, SCHEMA, path)
