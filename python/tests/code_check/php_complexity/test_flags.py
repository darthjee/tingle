"""Unit tests for code_check.php_complexity.flags.FLAGS."""

from __future__ import annotations

import pytest

from code_check.php_complexity.flags import FLAGS
from common.arg_parser import ArgParser


def _flag(name):
    return next(f for f in FLAGS if f["name"] == name)


def test_flag_names_in_order():
    assert [f["name"] for f in FLAGS] == [
        "path", "--warn", "--error", "--critical", "--top",
        "--min-level", "--fail-on", "--image",
    ]


def test_single_value_flags_default_to_none():
    parsed = ArgParser(FLAGS).parse(["src"])

    assert parsed == {
        "path": "src",
        "warn": None,
        "error": None,
        "critical": None,
        "top": None,
        "min_level": None,
        "fail_on": None,
        "image": None,
    }


def test_thresholds_parse_as_floats():
    parsed = ArgParser(FLAGS).parse(["src", "--warn", "2.5", "--error", "40", "--critical", "6e1"])

    assert parsed["warn"] == 2.5
    assert parsed["error"] == 40.0
    assert isinstance(parsed["error"], float)
    assert parsed["critical"] == 60.0


def test_top_parses_as_int():
    assert ArgParser(FLAGS).parse(["src", "--top", "3"])["top"] == 3


def test_types():
    assert _flag("--warn")["type"] is float
    assert _flag("--error")["type"] is float
    assert _flag("--critical")["type"] is float
    assert _flag("--top")["type"] is int
    assert _flag("--image")["type"] is str


def test_choices():
    assert _flag("--min-level")["choices"] == ["ok", "warn", "error", "critical"]
    assert _flag("--fail-on")["choices"] == ["warn", "error", "critical"]


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("path", "PHP file or directory to analyse (recursive)"),
        ("--warn", "Warn threshold on the file's total CCN (default: 20)"),
        ("--error", "Error threshold on the file's total CCN (default: 40)"),
        ("--critical", "Critical threshold on the file's total CCN (default: 60)"),
        ("--top", "Show only the top N most complex files (default: 0 = all)"),
        ("--min-level", "Show only files at this level or higher (default: ok)"),
        ("--fail-on", "Exit with status 2 if any file reaches this level or higher"),
        (
            "--image",
            "Docker image to run (default: darthjee/tingle_php_complexity:<tingle version>)",
        ),
    ],
)
def test_help_texts_match_spec(name, text):
    assert _flag(name)["help"] == text


@pytest.mark.parametrize(
    "name",
    [
        "--exclude", "--no-default-excludes", "--no-gitignore", "--ignore",
        "--include", "--no-config", "--details", "--ext",
    ],
)
def test_later_flags_are_absent(name):
    assert all(f["name"] != name for f in FLAGS)


@pytest.mark.parametrize("args", [["src", "--min-level", "bad"], ["src", "--fail-on", "ok"]])
def test_bad_choice_is_a_usage_error(args):
    with pytest.raises(SystemExit):
        ArgParser(FLAGS).parse(args)
