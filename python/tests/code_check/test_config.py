"""Unit tests for code_check.config (default_path, load_section, ConfigError)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from code_check.config import ConfigError, default_path, load_section


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
