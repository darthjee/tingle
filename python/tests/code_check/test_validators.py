"""Unit tests for code_check.validators (shared config value validators)."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.config import ConfigError
from code_check.validators import (
    boolean,
    list_of_str,
    non_empty_str,
    non_negative_int,
    non_negative_number,
    nullable_non_negative_int,
    one_of,
    validate_section,
)

# --- non_negative_int ------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 1, 250])
def test_non_negative_int_accepts(value):
    assert non_negative_int("top", value) is None


@pytest.mark.parametrize("value", [-1, 1.0, 1.5, True, False, "1", None, [1]])
def test_non_negative_int_rejects(value):
    assert non_negative_int("top", value) == "'top' must be an integer >= 0"


# --- nullable_non_negative_int ---------------------------------------------------


@pytest.mark.parametrize("value", [None, 0, 5])
def test_nullable_non_negative_int_accepts(value):
    assert nullable_non_negative_int("details", value) is None


@pytest.mark.parametrize("value", [-1, 1.0, True, False, "3", []])
def test_nullable_non_negative_int_rejects(value):
    assert nullable_non_negative_int("details", value) == (
        "'details' must be an integer >= 0 or null"
    )


# --- non_negative_number ---------------------------------------------------------


@pytest.mark.parametrize("value", [0, 0.0, 1, 1.5, 400.5, 1e9])
def test_non_negative_number_accepts(value):
    assert non_negative_number("warn", value) is None


@pytest.mark.parametrize(
    "value",
    [True, False, float("nan"), float("inf"), float("-inf"), -1, -0.5, "1", None, [1]],
)
def test_non_negative_number_rejects(value):
    assert non_negative_number("warn", value) == "'warn' must be a number >= 0"


# --- non_empty_str ---------------------------------------------------------------


@pytest.mark.parametrize("value", ["img", " img:1 ", "darthjee/tingle_rubycritic:0.6.0"])
def test_non_empty_str_accepts(value):
    assert non_empty_str("image", value) is None


@pytest.mark.parametrize("value", ["", "  ", "\t\n", 1, None, True, ["img"]])
def test_non_empty_str_rejects(value):
    assert non_empty_str("image", value) == "'image' must be a non-empty string"


# --- list_of_str -----------------------------------------------------------------


@pytest.mark.parametrize("value", [[], ["a"], ["a", "b"]])
def test_list_of_str_accepts(value):
    assert list_of_str("ignore", value) is None


@pytest.mark.parametrize("value", ["a", ["a", 1], [None], {"a": 1}, None])
def test_list_of_str_rejects(value):
    assert list_of_str("ignore", value) == "'ignore' must be a list of strings"


# --- boolean ---------------------------------------------------------------------


@pytest.mark.parametrize("value", [True, False])
def test_boolean_accepts(value):
    assert boolean("gitignore", value) is None


@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_boolean_rejects(value):
    assert boolean("gitignore", value) == "'gitignore' must be a boolean"


# --- one_of ----------------------------------------------------------------------


def test_one_of_nullable():
    check = one_of(["warn", "error", "critical"], nullable=True)

    assert check("fail_on", None) is None
    assert check("fail_on", "error") is None
    assert check("fail_on", "ok") == "'fail_on' must be one of warn, error, critical or null"
    assert check("fail_on", 1) == "'fail_on' must be one of warn, error, critical or null"


def test_one_of_not_nullable():
    check = one_of(["ok", "warn", "error", "critical"])

    assert check("min_level", "ok") is None
    assert check("min_level", None) == "'min_level' must be one of ok, warn, error or critical"


# --- validate_section ------------------------------------------------------------

SCHEMA = {"top": non_negative_int, "gitignore": boolean}
PATH = Path("/home/me/.tingle/code_check/config.json")


def test_validate_section_returns_section_unchanged():
    section = {"top": 3, "gitignore": False}

    assert validate_section(section, SCHEMA, PATH) is section


def test_validate_section_unknown_key():
    with pytest.raises(ConfigError) as exc_info:
        validate_section({"ext": [".rb"]}, SCHEMA, PATH)

    assert exc_info.value.path == PATH
    assert exc_info.value.reason == "unknown key 'ext'"
    assert str(exc_info.value) == f"{PATH}: unknown key 'ext'"


def test_validate_section_reports_first_bad_key_in_section_order():
    with pytest.raises(ConfigError) as exc_info:
        validate_section({"gitignore": 1, "top": -1}, SCHEMA, PATH)

    assert exc_info.value.reason == "'gitignore' must be a boolean"
