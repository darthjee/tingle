"""Unit tests for code_check.rubycritic.flags.FLAGS."""

from __future__ import annotations

import pytest

from code_check.rubycritic.flags import FLAGS
from common.arg_parser import ArgParser


def _flag(name):
    return next(f for f in FLAGS if f["name"] == name)


def test_flag_names_in_order():
    assert [f["name"] for f in FLAGS] == [
        "path", "--warn", "--error", "--critical", "--top",
        "--min-level", "--fail-on", "--image",
    ]


def test_single_value_flags_default_to_none():
    parsed = ArgParser(FLAGS).parse(["app"])

    assert parsed == {
        "path": "app",
        "warn": None,
        "error": None,
        "critical": None,
        "top": None,
        "min_level": None,
        "fail_on": None,
        "image": None,
    }


def test_thresholds_parse_as_floats():
    parsed = ArgParser(FLAGS).parse(["app", "--warn", "12.5", "--error", "20", "--critical", "3e2"])

    assert parsed["warn"] == 12.5
    assert parsed["error"] == 20.0
    assert isinstance(parsed["error"], float)
    assert parsed["critical"] == 300.0


def test_choices():
    assert _flag("--min-level")["choices"] == ["ok", "warn", "error", "critical"]
    assert _flag("--fail-on")["choices"] == ["warn", "error", "critical"]


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("path", "Ruby file or directory to analyse (recursive)"),
        ("--warn", "Warn threshold on the file's total Flog complexity (default: 100)"),
        ("--error", "Error threshold on the file's total Flog complexity (default: 200)"),
        ("--critical", "Critical threshold on the file's total Flog complexity (default: 400)"),
        ("--top", "Show only the top N most complex files (default: 0 = all)"),
        ("--min-level", "Show only files at this level or higher (default: ok)"),
        ("--fail-on", "Exit with status 2 if any file reaches this level or higher"),
        ("--image", "Docker image to run (default: darthjee/tingle_rubycritic:<tingle version>)"),
    ],
)
def test_help_texts_match_spec(name, text):
    assert _flag(name)["help"] == text
