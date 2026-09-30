"""config.py — Load ~/.tingle/code_check/config.json.

The config file is a JSON object whose top-level keys are sections, one per
code_check subcommand. `load_section` is generic and knows nothing about any
section's keys; each subcommand validates its own section.

Dependencies: standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
