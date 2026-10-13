"""Unit tests for code_check.js_complexity.flags.FLAGS."""

from __future__ import annotations

import pytest

from code_check.js_complexity.constants import Constants
from code_check.js_complexity.flags import FLAGS
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
    parsed = ArgParser(FLAGS).parse(["src"])

    assert parsed == {
        "path": "src",
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
    parsed = ArgParser(FLAGS).parse(["src", "--warn", "12.5", "--error", "20", "--critical", "3e1"])

    assert parsed["warn"] == 12.5
    assert parsed["error"] == 20.0
    assert isinstance(parsed["error"], float)
    assert parsed["critical"] == 30.0


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
        ("path", "JavaScript/TypeScript file or directory to analyse (recursive)"),
        ("--warn", "Warn threshold on the file's FTA score (default: 50)"),
        ("--error", "Error threshold on the file's FTA score (default: 60)"),
        ("--critical", "Critical threshold on the file's FTA score (default: 75)"),
        ("--top", "Show only the top N most complex files (default: 0 = all)"),
        ("--min-level", "Show only files at this level or higher (default: ok)"),
        ("--fail-on", "Exit with status 2 if any file reaches this level or higher"),
        (
            "--details",
            (
                "Show the N most complex functions under each file "
                "(default when given without N: 5; 0 = all)"
            ),
        ),
        (
            "--image",
            "Docker image to run (default: darthjee/tingle_js_complexity:<tingle version>)",
        ),
        (
            "--exclude",
            (
                "Extra directory names to skip (comma-separated), added to the defaults: "
                "node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,"
                ".cache,coverage,.nuxt,out,target,.turbo,.svelte-kit,.output,.vercel,"
                ".parcel-cache,storybook-static"
            ),
        ),
        (
            "--no-default-excludes",
            "Do not skip the default directories or minified bundles; only --exclude names apply",
        ),
        (
            "--no-gitignore",
            "Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)",
        ),
        ("--no-config", "Do not read ~/.tingle/code_check/config.json"),
        ("--ignore", "Skip files whose path relative to <path> matches this glob (can be repeated)"),
        (
            "--include",
            (
                "Only analyse JavaScript/TypeScript files whose path relative to <path> "
                "matches this glob (can be repeated)"
            ),
        ),
    ],
)
def test_help_texts_match_spec(name, text):
    assert _flag(name)["help"] == text


def test_exclude_help_lists_every_default():
    help_text = _flag("--exclude")["help"]

    assert help_text.endswith(",".join(Constants.DEFAULT_EXCLUDES))


def test_selection_flag_shapes():
    assert _flag("--exclude")["type"] is str
    assert _flag("--exclude")["default"] is None
    assert "action" not in _flag("--exclude")
    assert _flag("--no-default-excludes")["action"] == "store_true"
    assert _flag("--no-gitignore")["action"] == "store_true"
    for name in ("--ignore", "--include"):
        assert _flag(name)["type"] is str
        assert _flag(name)["action"] == "append"
        assert _flag(name)["default"] is None


def test_exclude_is_not_repeatable_last_wins():
    parsed = ArgParser(FLAGS).parse(["src", "--exclude", "a,b", "--exclude", "c"])

    assert parsed["exclude"] == "c"


def test_ignore_and_include_are_repeatable():
    parsed = ArgParser(FLAGS).parse(
        ["src", "--ignore", "a", "--ignore", "b", "--include", "x", "--include", "y"]
    )

    assert parsed["ignore"] == ["a", "b"]
    assert parsed["include"] == ["x", "y"]


def test_store_true_flags():
    parsed = ArgParser(FLAGS).parse(["src", "--no-default-excludes", "--no-gitignore"])

    assert parsed["no_default_excludes"] is True
    assert parsed["no_gitignore"] is True


def test_no_config_flag():
    assert _flag("--no-config")["action"] == "store_true"
    assert FLAGS[-1]["name"] == "--no-config"
    assert ArgParser(FLAGS).parse(["src", "--no-config"])["no_config"] is True
    assert ArgParser(FLAGS).parse(["src"])["no_config"] is False


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["src"], None),
        (["src", "--details"], 5),
        (["src", "--details", "3"], 3),
        (["src", "--details", "0"], 0),
        (["--details", "2", "src"], 2),
    ],
)
def test_details_values(args, expected):
    assert ArgParser(FLAGS).parse(args)["details"] == expected


def test_details_flag_shape():
    assert _flag("--details")["type"] is int
    assert _flag("--details")["nargs"] == "?"
    assert _flag("--details")["const"] == Constants.DEFAULT_DETAILS == 5


def test_details_rejects_non_int():
    with pytest.raises(SystemExit):
        ArgParser(FLAGS).parse(["src", "--details", "x"])


def test_ext_flag_is_absent():
    assert all(f["name"] != "--ext" for f in FLAGS)


@pytest.mark.parametrize("args", [["src", "--min-level", "bad"], ["src", "--fail-on", "ok"]])
def test_bad_choice_is_a_usage_error(args):
    with pytest.raises(SystemExit):
        ArgParser(FLAGS).parse(args)
