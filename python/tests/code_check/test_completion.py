"""Unit tests for code_check.completion.complete."""

from __future__ import annotations

import subprocess  # nosec B404 - runs the test interpreter only
import sys
from pathlib import Path

import pytest

from code_check.completion import FILES_SENTINEL, complete
from code_check.executor import CodeCheck
from code_check.file_size.flags import FLAGS
from code_check.rubycritic.flags import FLAGS as RUBYCRITIC_FLAGS
from code_check.subcommands import SUBCOMMAND_NAMES

EXPECTED_FLAGS = [f["name"] for f in FLAGS if f["name"].startswith("-")]
CHOICE_FLAGS = {f["name"]: f["choices"] for f in FLAGS if f.get("choices")}
FREE_VALUE_FLAGS = [
    f["name"]
    for f in FLAGS
    if f["name"].startswith("-") and f.get("action") != "store_true" and not f.get("choices")
]
STORE_TRUE_FLAGS = [f["name"] for f in FLAGS if f.get("action") == "store_true"]


# --- derived from FLAGS / SUBCOMMANDS -------------------------------------------


def test_subcommand_names_match_executor_table():
    assert tuple(CodeCheck.SUBCOMMANDS) == SUBCOMMAND_NAMES


def test_flag_groups_cover_the_documented_flags():
    assert set(CHOICE_FLAGS) == {"--min-level", "--fail-on"}
    assert set(FREE_VALUE_FLAGS) == {
        "--warn", "--error", "--critical", "--top", "--exclude", "--ignore", "--include", "--ext",
    }
    assert set(STORE_TRUE_FLAGS) == {"--no-default-excludes", "--no-gitignore", "--no-config"}


def test_completion_imports_no_heavy_module():
    code = (
        "import sys; import code_check.completion; "
        "heavy = [m for m in ('code_check.executor', 'code_check.file_size.executor', "
        "'code_check.file_size.file_collector', 'code_check.config', "
        "'code_check.file_size.config', 'code_check.file_size.reporter', "
        "'code_check.rubycritic.executor', 'code_check.rubycritic.docker_runner', "
        "'code_check.rubycritic.output_parser', 'code_check.rubycritic.reporter', "
        "'code_check.rubycritic.selection') if m in sys.modules]; "
        "print(','.join(heavy))"
    )
    python_dir = Path(__file__).resolve().parents[2]
    result = subprocess.run(  # nosec B603 - fixed interpreter and arguments
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, cwd=python_dir
    )

    assert result.stdout.strip() == ""


# --- before the subcommand ------------------------------------------------------


@pytest.mark.parametrize("argv", [[], [""], ["fi"]])
def test_subcommand_position_returns_names(argv):
    assert complete(argv) == list(SUBCOMMAND_NAMES)


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_after_help_flag_returns_names(flag):
    assert complete([flag, ""]) == list(SUBCOMMAND_NAMES)


@pytest.mark.parametrize("argv", [["--warn", ""], ["--warn", "100", ""], ["-x", "file_size", ""]])
def test_flag_before_subcommand_returns_nothing(argv):
    assert complete(argv) == []


@pytest.mark.parametrize("name", ["nope", "File_Size", "file-size"])
def test_unknown_subcommand_returns_nothing(name):
    assert complete([name, ""]) == []


# --- file_size: path vs flags ---------------------------------------------------


@pytest.mark.parametrize("current", ["", "src", "./sr"])
def test_file_size_without_path_returns_file_sentinel(current):
    assert complete(["file_size", current]) == [FILES_SENTINEL]


def test_help_then_file_size_behaves_like_file_size():
    assert complete(["-h", "file_size", ""]) == [FILES_SENTINEL]


@pytest.mark.parametrize("current", ["-", "--", "--w"])
def test_file_size_dash_word_returns_every_flag(current):
    assert complete(["file_size", current]) == EXPECTED_FLAGS


def test_file_size_after_path_returns_every_flag():
    assert complete(["file_size", ".", ""]) == EXPECTED_FLAGS


def test_used_flags_are_still_suggested():
    assert complete(["file_size", ".", "--ext", ".py", ""]) == EXPECTED_FLAGS


# --- file_size: flag values -----------------------------------------------------


@pytest.mark.parametrize("flag", sorted(CHOICE_FLAGS))
def test_after_choice_flag_returns_its_choices(flag):
    assert complete(["file_size", ".", flag, ""]) == CHOICE_FLAGS[flag]


def test_fail_on_choices():
    assert complete(["file_size", ".", "--fail-on", ""]) == ["warn", "error", "critical"]


@pytest.mark.parametrize("flag", FREE_VALUE_FLAGS)
def test_after_free_value_flag_returns_nothing(flag):
    assert complete(["file_size", ".", flag, ""]) == []


def test_value_flag_before_path_does_not_count_as_path():
    assert complete(["file_size", "--warn", "100", ""]) == [FILES_SENTINEL]


def test_flag_value_is_not_taken_as_a_flag():
    # `--exclude --warn`: `--warn` is the value of `--exclude`, not a pending flag.
    assert complete(["file_size", "--exclude", "--warn", ""]) == [FILES_SENTINEL]


@pytest.mark.parametrize("flag", STORE_TRUE_FLAGS)
def test_after_store_true_flag_without_path_returns_file_sentinel(flag):
    assert complete(["file_size", flag, ""]) == [FILES_SENTINEL]


@pytest.mark.parametrize("flag", STORE_TRUE_FLAGS)
def test_after_store_true_flag_with_path_returns_every_flag(flag):
    assert complete(["file_size", ".", flag, ""]) == EXPECTED_FLAGS


# --- sentinel is never mixed ----------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        [""],
        ["file_size", ""],
        ["file_size", "-"],
        ["file_size", ".", ""],
        ["file_size", ".", "--fail-on", ""],
        ["file_size", "--no-config", ""],
        ["nope", ""],
    ],
)
def test_file_sentinel_is_never_mixed_with_words(argv):
    result = complete(argv)

    assert result == [FILES_SENTINEL] or FILES_SENTINEL not in result


# --- rubycritic -------------------------------------------------------------------

RUBYCRITIC_EXPECTED_FLAGS = [f["name"] for f in RUBYCRITIC_FLAGS if f["name"].startswith("-")]


def test_rubycritic_flag_names():
    assert RUBYCRITIC_EXPECTED_FLAGS == [
        "--warn", "--error", "--critical", "--top", "--min-level", "--fail-on", "--details",
        "--image",
    ]


@pytest.mark.parametrize("current", ["", "app", "./ap"])
def test_rubycritic_without_path_returns_file_sentinel(current):
    assert complete(["rubycritic", current]) == [FILES_SENTINEL]


def test_help_then_rubycritic_behaves_like_rubycritic():
    assert complete(["-h", "rubycritic", ""]) == [FILES_SENTINEL]


@pytest.mark.parametrize("current", ["-", "--i"])
def test_rubycritic_dash_word_returns_every_flag(current):
    assert complete(["rubycritic", current]) == RUBYCRITIC_EXPECTED_FLAGS


def test_rubycritic_after_path_returns_every_flag():
    assert complete(["rubycritic", "app", ""]) == RUBYCRITIC_EXPECTED_FLAGS


@pytest.mark.parametrize(
    ("flag", "choices"),
    [
        ("--min-level", ["ok", "warn", "error", "critical"]),
        ("--fail-on", ["warn", "error", "critical"]),
    ],
)
def test_rubycritic_choice_flags_return_choices(flag, choices):
    assert complete(["rubycritic", "app", flag, ""]) == choices


@pytest.mark.parametrize(
    "flag", ["--warn", "--error", "--critical", "--top", "--details", "--image"],
)
def test_rubycritic_free_value_flags_return_nothing(flag):
    assert complete(["rubycritic", "app", flag, ""]) == []


def test_rubycritic_value_flag_before_path_does_not_count_as_path():
    assert complete(["rubycritic", "--image", "img:dev", ""]) == [FILES_SENTINEL]


def test_rubycritic_does_not_offer_file_size_only_flags():
    flags = complete(["rubycritic", "app", ""])

    assert "--ext" not in flags
    assert "--no-config" not in flags
