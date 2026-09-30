"""Unit tests for code_check.file_size.config (SCHEMA, validate)."""

from __future__ import annotations

import pytest

from code_check.config import ConfigError as GenericConfigError
from code_check.file_size.config import SCHEMA, ConfigError, validate


def test_config_error_is_reexported_from_generic_config():
    assert ConfigError is GenericConfigError


# --- validate -------------------------------------------------------------------

VALID_SECTION = {
    "warn": 1,
    "error": 2,
    "critical": 0,
    "top": 5,
    "exclude": ["fixtures"],
    "ignore": ["*.lock"],
    "include": [],
    "ext": [".py", ".js"],
    "no_default_excludes": True,
    "gitignore": False,
    "fail_on": "error",
    "min_level": "warn",
}


def test_schema_covers_every_contract_key():
    assert set(SCHEMA) == set(VALID_SECTION)


def test_validate_accepts_every_key_and_returns_section_unchanged(tmp_path):
    section = dict(VALID_SECTION)

    assert validate(section, tmp_path / "c.json") == VALID_SECTION


def test_validate_accepts_empty_section(tmp_path):
    assert validate({}, tmp_path / "c.json") == {}


@pytest.mark.parametrize("value", [None, "warn", "error", "critical"])
def test_validate_fail_on_accepts_levels_and_null(tmp_path, value):
    assert validate({"fail_on": value}, tmp_path / "c.json") == {"fail_on": value}


@pytest.mark.parametrize("value", ["ok", "warn", "error", "critical"])
def test_validate_min_level_accepts_levels(tmp_path, value):
    assert validate({"min_level": value}, tmp_path / "c.json") == {"min_level": value}


@pytest.mark.parametrize("key", ["path", "wran", "no_gitignore", "no-config"])
def test_validate_unknown_key_raises(tmp_path, key):
    path = tmp_path / "c.json"

    with pytest.raises(ConfigError) as exc_info:
        validate({key: 1}, path)

    assert exc_info.value.reason == f"unknown key '{key}'"
    assert exc_info.value.path == path


INT_REASON = "must be an integer >= 0"
LIST_REASON = "must be a list of strings"
BOOL_REASON = "must be a boolean"
FAIL_ON_REASON = "must be one of warn, error, critical or null"
MIN_LEVEL_REASON = "must be one of ok, warn, error or critical"


@pytest.mark.parametrize(
    ("key", "value", "reason"),
    [
        *[(k, v, INT_REASON) for k in ("warn", "error", "critical", "top")
          for v in (True, False, -1, 1.5, "10", None, [1])],
        *[(k, v, LIST_REASON) for k in ("exclude", "ignore", "include", "ext")
          for v in ("a", ["a", 1], [None], {"a": 1}, None, True)],
        *[(k, v, BOOL_REASON) for k in ("no_default_excludes", "gitignore")
          for v in (0, 1, "true", None, [])],
        *[("fail_on", v, FAIL_ON_REASON) for v in ("ok", "WARN", "", 2, True, [])],
        *[("min_level", v, MIN_LEVEL_REASON) for v in (None, "info", "OK", 0, False)],
    ],
)
def test_validate_wrong_type_or_value_raises(tmp_path, key, value, reason):
    with pytest.raises(ConfigError) as exc_info:
        validate({key: value}, tmp_path / "c.json")

    assert exc_info.value.reason == f"'{key}' {reason}"


def test_validate_bool_is_not_an_integer(tmp_path):
    with pytest.raises(ConfigError, match="'top' must be an integer >= 0"):
        validate({"top": True}, tmp_path / "c.json")
