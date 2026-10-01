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
        "--min-level", "--fail-on", "--details", "--image",
        "--exclude", "--no-default-excludes", "--no-gitignore", "--ignore", "--include",
        "--no-config",
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
        "details": None,
        "image": None,
        "exclude": None,
        "no_default_excludes": False,
        "no_gitignore": False,
        "ignore": None,
        "include": None,
        "no_config": False,
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
        (
            "--details",
            (
                "Show the N most complex methods under each file "
                "(default when given without N: 5; 0 = all)"
            ),
        ),
        ("--image", "Docker image to run (default: darthjee/tingle_rubycritic:<tingle version>)"),
        (
            "--exclude",
            (
                "Extra directory names to skip (comma-separated), added to the defaults: "
                "node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,"
                ".cache,coverage,.nuxt,out,target,tmp,log,.bundle"
            ),
        ),
        ("--no-default-excludes", "Do not skip the default directories; only --exclude names apply"),
        (
            "--no-gitignore",
            "Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)",
        ),
        ("--ignore", "Skip files whose path relative to <path> matches this glob (can be repeated)"),
        (
            "--include",
            "Only analyse .rb files whose path relative to <path> matches this glob (can be repeated)",
        ),
        ("--no-config", "Do not read ~/.tingle/code_check/config.json"),
    ],
)
def test_help_texts_match_spec(name, text):
    assert _flag(name)["help"] == text


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["app"], None),
        (["app", "--details"], 5),
        (["app", "--details", "3"], 3),
        (["app", "--details", "0"], 0),
        (["--details", "2", "app"], 2),
    ],
)
def test_details_values(args, expected):
    assert ArgParser(FLAGS).parse(args)["details"] == expected


def test_exclude_is_not_repeatable_last_wins():
    parsed = ArgParser(FLAGS).parse(["app", "--exclude", "a,b", "--exclude", "c"])

    assert parsed["exclude"] == "c"


def test_ignore_and_include_are_repeatable():
    parsed = ArgParser(FLAGS).parse(
        ["app", "--ignore", "a", "--ignore", "b", "--include", "x", "--include", "y"]
    )

    assert parsed["ignore"] == ["a", "b"]
    assert parsed["include"] == ["x", "y"]


def test_store_true_flags():
    parsed = ArgParser(FLAGS).parse(
        ["app", "--no-default-excludes", "--no-gitignore", "--no-config"]
    )

    assert parsed["no_default_excludes"] is True
    assert parsed["no_gitignore"] is True
    assert parsed["no_config"] is True


def test_no_config_is_the_last_flag():
    assert FLAGS[-1] == {
        "name": "--no-config",
        "action": "store_true",
        "help": "Do not read ~/.tingle/code_check/config.json",
    }


def test_no_ext_flag():
    assert all(f["name"] != "--ext" for f in FLAGS)
