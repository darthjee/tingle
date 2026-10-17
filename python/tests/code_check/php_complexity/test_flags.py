"""Unit tests for code_check.php_complexity.flags.FLAGS."""

from __future__ import annotations

import pytest

from code_check.php_complexity.constants import Constants
from code_check.php_complexity.flags import FLAGS
from common.arg_parser import ArgParser


def _flag(name):
    return next(f for f in FLAGS if f["name"] == name)


def test_flag_names_in_order():
    assert [f["name"] for f in FLAGS] == [
        "path", "--warn", "--error", "--critical", "--top",
        "--min-level", "--fail-on", "--image", "--exclude", "--no-default-excludes",
        "--no-gitignore", "--ignore", "--include",
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
        "exclude": None,
        "no_default_excludes": False,
        "no_gitignore": False,
        "ignore": None,
        "include": None,
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
    assert _flag("--exclude")["type"] is str
    assert _flag("--ignore")["type"] is str
    assert _flag("--include")["type"] is str


def test_actions():
    assert "action" not in _flag("--exclude")
    assert _flag("--no-default-excludes")["action"] == "store_true"
    assert _flag("--no-gitignore")["action"] == "store_true"
    assert _flag("--ignore")["action"] == "append"
    assert _flag("--include")["action"] == "append"


def test_selection_flags_parse():
    parsed = ArgParser(FLAGS).parse([
        "src", "--exclude", "a,b", "--exclude", "c", "--no-default-excludes",
        "--no-gitignore", "--ignore", "x/**", "--ignore", "*.gen.php",
        "--include", "src/**", "--include", "lib/**",
    ])

    assert parsed["exclude"] == "c"
    assert parsed["no_default_excludes"] is True
    assert parsed["no_gitignore"] is True
    assert parsed["ignore"] == ["x/**", "*.gen.php"]
    assert parsed["include"] == ["src/**", "lib/**"]


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
        (
            "--exclude",
            "Extra directory names to skip (comma-separated), added to the defaults: "
            "node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,"
            ".cache,coverage,.nuxt,out,target,var,storage,.phpunit.cache",
        ),
        (
            "--no-default-excludes",
            "Do not skip the default directories or bootstrap/cache; "
            "only --exclude names apply",
        ),
        (
            "--no-gitignore",
            "Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)",
        ),
        (
            "--ignore",
            "Skip files whose path relative to <path> matches this glob (can be repeated)",
        ),
        (
            "--include",
            "Only analyse PHP files whose path relative to <path> matches this glob "
            "(can be repeated)",
        ),
    ],
)
def test_help_texts_match_spec(name, text):
    assert _flag(name)["help"] == text


@pytest.mark.parametrize("name", ["--no-config", "--details", "--ext"])
def test_later_flags_are_absent(name):
    assert all(f["name"] != name for f in FLAGS)


def test_exclude_help_lists_all_sixteen_defaults():
    assert len(Constants.DEFAULT_EXCLUDES) == 16
    help_text = _flag("--exclude")["help"]
    assert help_text.endswith(",".join(Constants.DEFAULT_EXCLUDES))


@pytest.mark.parametrize("args", [["src", "--min-level", "bad"], ["src", "--fail-on", "ok"]])
def test_bad_choice_is_a_usage_error(args):
    with pytest.raises(SystemExit):
        ArgParser(FLAGS).parse(args)
