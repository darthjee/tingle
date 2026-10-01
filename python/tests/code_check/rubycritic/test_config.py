"""Unit tests for code_check.rubycritic.config (the rubycritic config section)."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.config import ConfigError as GenericConfigError
from code_check.rubycritic.config import SCHEMA, ConfigError, validate

PATH = Path("/home/me/.tingle/code_check/config.json")

FULL_SECTION = {
    "warn": 100,
    "error": 200,
    "critical": 400.5,
    "top": 20,
    "exclude": ["db"],
    "no_default_excludes": False,
    "ignore": ["spec/fixtures/**"],
    "include": ["app/**", "lib/**"],
    "gitignore": True,
    "fail_on": "error",
    "min_level": "warn",
    "image": "darthjee/tingle_rubycritic:0.6.0",
    "details": 5,
}


def _reason(section):
    with pytest.raises(ConfigError) as exc_info:
        validate(section, PATH)
    assert exc_info.value.path == PATH
    assert str(exc_info.value) == f"{PATH}: {exc_info.value.reason}"
    return exc_info.value.reason


def test_config_error_is_the_generic_one():
    assert ConfigError is GenericConfigError


def test_schema_keys():
    assert list(SCHEMA) == [
        "warn", "error", "critical", "top", "exclude", "ignore", "include",
        "no_default_excludes", "gitignore", "fail_on", "min_level", "image", "details",
    ]


def test_full_section_is_valid_and_returned_unchanged():
    assert validate(FULL_SECTION, PATH) is FULL_SECTION


def test_empty_section_is_valid():
    assert validate({}, PATH) == {}


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("warn", 0),
        ("warn", 12.5),
        ("error", 0.0),
        ("critical", 1000),
        ("top", 0),
        ("top", 10),
        ("exclude", []),
        ("ignore", ["a", "b"]),
        ("include", []),
        ("no_default_excludes", True),
        ("gitignore", False),
        ("fail_on", None),
        ("fail_on", "warn"),
        ("fail_on", "critical"),
        ("min_level", "ok"),
        ("min_level", "critical"),
        ("image", "img:dev"),
        ("details", None),
        ("details", 0),
        ("details", 3),
    ],
)
def test_valid_values(key, value):
    assert validate({key: value}, PATH) == {key: value}


@pytest.mark.parametrize(
    ("key", "value", "reason"),
    [
        ("warn", -1, "'warn' must be a number >= 0"),
        ("warn", True, "'warn' must be a number >= 0"),
        ("warn", float("nan"), "'warn' must be a number >= 0"),
        ("warn", "100", "'warn' must be a number >= 0"),
        ("error", float("inf"), "'error' must be a number >= 0"),
        ("error", False, "'error' must be a number >= 0"),
        ("critical", -0.5, "'critical' must be a number >= 0"),
        ("critical", None, "'critical' must be a number >= 0"),
        ("top", -1, "'top' must be an integer >= 0"),
        ("top", 1.5, "'top' must be an integer >= 0"),
        ("top", True, "'top' must be an integer >= 0"),
        ("exclude", "db", "'exclude' must be a list of strings"),
        ("ignore", [1], "'ignore' must be a list of strings"),
        ("include", None, "'include' must be a list of strings"),
        ("no_default_excludes", "yes", "'no_default_excludes' must be a boolean"),
        ("gitignore", 1, "'gitignore' must be a boolean"),
        ("fail_on", "ok", "'fail_on' must be one of warn, error, critical or null"),
        ("min_level", None, "'min_level' must be one of ok, warn, error or critical"),
        ("min_level", "info", "'min_level' must be one of ok, warn, error or critical"),
        ("image", "", "'image' must be a non-empty string"),
        ("image", "   ", "'image' must be a non-empty string"),
        ("image", 1, "'image' must be a non-empty string"),
        ("details", -1, "'details' must be an integer >= 0 or null"),
        ("details", 2.0, "'details' must be an integer >= 0 or null"),
        ("details", True, "'details' must be an integer >= 0 or null"),
    ],
)
def test_invalid_values(key, value, reason):
    assert _reason({key: value}) == reason


def test_ext_is_an_unknown_key():
    assert _reason({"ext": [".rb"]}) == "unknown key 'ext'"


def test_unknown_key():
    assert _reason({"no_config": True}) == "unknown key 'no_config'"


def test_first_bad_key_in_section_order_wins():
    assert _reason({"warn": 1, "image": "", "top": -1}) == "'image' must be a non-empty string"
    assert _reason({"ext": [], "warn": -1}) == "unknown key 'ext'"


def test_thresholds_are_not_compared():
    section = {"warn": 500, "error": 10, "critical": 1}

    assert validate(section, PATH) is section
