"""Unit tests for check_file_size.config (load_section, SCHEMA, validate)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from check_file_size.config import SCHEMA, ConfigError, default_path, load_section, validate


def _write(path: Path, content) -> Path:
    """Write `content` (JSON-encoded unless already a str) to `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content))
    return path


# --- default_path ---------------------------------------------------------------


def test_default_path_follows_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    assert default_path() == tmp_path / ".tingle" / "code_check" / "config.json"


def test_load_section_uses_default_path_under_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    _write(tmp_path / ".tingle" / "code_check" / "config.json", {"check_file_size": {"top": 3}})

    assert load_section("check_file_size") == {"top": 3}


def test_load_section_default_path_missing_returns_none():
    assert load_section("check_file_size") is None


# --- load_section ---------------------------------------------------------------


def test_load_section_missing_file_returns_none(tmp_path):
    assert load_section("check_file_size", tmp_path / "nope.json") is None


def test_load_section_missing_section_returns_none(tmp_path):
    path = _write(tmp_path / "c.json", {"code_check": {"x": 1}})

    assert load_section("check_file_size", path) is None


def test_load_section_empty_section_returns_empty_dict(tmp_path):
    path = _write(tmp_path / "c.json", {"check_file_size": {}})

    assert load_section("check_file_size", path) == {}


def test_load_section_ignores_other_top_level_keys(tmp_path):
    path = _write(
        tmp_path / "c.json",
        {"code_check": "anything", "other": [1, 2], "check_file_size": {"warn": 10}},
    )

    assert load_section("check_file_size", path) == {"warn": 10}


def test_load_section_does_not_validate_section_keys(tmp_path):
    path = _write(tmp_path / "c.json", {"check_file_size": {"unknown": True}})

    assert load_section("check_file_size", path) == {"unknown": True}


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        ("{not json", "invalid JSON"),
        ("", "invalid JSON"),
        ("[]", "top level must be an object"),
        ("null", "top level must be an object"),
        ('"text"', "top level must be an object"),
        ('{"check_file_size": []}', "'check_file_size' must be an object"),
        ('{"check_file_size": null}', "'check_file_size' must be an object"),
        ('{"check_file_size": 3}', "'check_file_size' must be an object"),
    ],
)
def test_load_section_file_level_errors(tmp_path, content, reason):
    path = _write(tmp_path / "c.json", content)

    with pytest.raises(ConfigError) as exc_info:
        load_section("check_file_size", path)

    assert exc_info.value.path == path
    assert reason in exc_info.value.reason
    assert str(exc_info.value).startswith(f"{path}: ")


def test_load_section_unreadable_file_raises(tmp_path):
    # A directory at the config path cannot be read as a file.
    path = tmp_path / "c.json"
    path.mkdir()

    with pytest.raises(ConfigError) as exc_info:
        load_section("check_file_size", path)

    assert "cannot read file" in exc_info.value.reason


def test_load_section_non_utf8_file_raises(tmp_path):
    path = tmp_path / "c.json"
    path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(ConfigError) as exc_info:
        load_section("check_file_size", path)

    assert "cannot read file" in exc_info.value.reason


def test_config_error_str_is_path_and_reason():
    err = ConfigError(Path("/x/config.json"), "boom")

    assert str(err) == "/x/config.json: boom"
    assert err.path == Path("/x/config.json")
    assert err.reason == "boom"


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
