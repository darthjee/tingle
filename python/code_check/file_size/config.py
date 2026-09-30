"""config.py — Load and validate ~/.tingle/code_check/config.json.

The config file is a JSON object whose top-level keys are sections, one per
tool (`check_file_size` today, more under the future `code_check` tool).
`load_section` is generic and knows nothing about any section's keys;
`SCHEMA` and `validate` hold the `check_file_size` rules.

Dependencies: standard library only.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

# A validator returns None when `value` is valid, else the reason it is not.
Validator = Callable[[str, Any], "str | None"]

# Returned by `_read_json` when the file does not exist (JSON `null` is valid).
_MISSING = object()


def default_path() -> Path:
    """Return the config file location, computed now so `HOME` changes apply."""
    return Path.home() / ".tingle" / "code_check" / "config.json"


class ConfigError(Exception):
    """A config file problem; `str()` gives `"<path>: <reason>"`."""

    def __init__(self, path: Path, reason: str) -> None:
        """Store the offending file `path` and a human-readable `reason`."""
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


def _read_json(path: Path) -> Any:
    """Parse the JSON file at `path`, or return `_MISSING` when it does not exist."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _MISSING
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(path, f"cannot read file: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(path, f"invalid JSON: {exc}") from exc


def load_section(name: str, path: Path | None = None) -> dict | None:
    """Return the `name` section of the config file at `path` (default: `default_path()`).

    Returns None when the file or the section is missing, so callers can tell
    "no section" from "empty section". Raises `ConfigError` when the file
    cannot be read, is not valid JSON, or when the top level or the section is
    not a JSON object.
    """
    path = path if path is not None else default_path()
    data = _read_json(path)
    if data is _MISSING:
        return None
    if not isinstance(data, dict):
        raise ConfigError(path, "top level must be an object")
    if name not in data:
        return None
    section = data[name]
    if not isinstance(section, dict):
        raise ConfigError(path, f"'{name}' must be an object")
    return section


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


# check_file_size section: key → validator.
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
    """Check a `check_file_size` section against `SCHEMA` and return it unchanged.

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
