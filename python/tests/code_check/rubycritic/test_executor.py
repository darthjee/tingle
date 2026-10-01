"""Unit tests for code_check.rubycritic.executor.CheckRubycritic (parse, validate, resolve)."""

from __future__ import annotations

import os

import pytest

from code_check.palette import Palette
from code_check.rubycritic.errors import RubycriticError
from code_check.rubycritic.executor import CheckRubycritic


def _run(args):
    with pytest.raises(SystemExit) as exc_info:
        CheckRubycritic().run(args)
    return exc_info.value.code


# --- help and usage errors ---------------------------------------------------------


def test_run_no_args_prints_help_and_exits_zero(capsys):
    assert _run([]) == 0

    out = capsys.readouterr().out
    assert out.startswith("usage: tingle code_check rubycritic ")
    assert "--image" in out


def test_run_help_exits_zero(capsys):
    assert _run(["-h"]) == 0

    assert capsys.readouterr().out.startswith("usage: tingle code_check rubycritic ")


@pytest.mark.parametrize(
    "args",
    [
        [".", "--warn", "x"],
        [".", "--top", "1.5"],
        [".", "--min-level", "bad"],
        [".", "--fail-on", "ok"],
        [".", "--unknown"],
    ],
)
def test_run_argparse_usage_errors_exit_one(capsys, args):
    assert _run(args) == 1

    assert "usage:" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--warn", "-1"], "Error: --warn must be a number >= 0"),
        (["--error", "-0.5"], "Error: --error must be a number >= 0"),
        (["--critical", "-3"], "Error: --critical must be a number >= 0"),
        (["--warn", "nan"], "Error: --warn must be a number >= 0"),
        (["--top", "-1"], "Error: --top must be an integer >= 0"),
        (["--image", ""], "Error: --image must not be empty"),
    ],
)
def test_run_validation_errors_exit_one(tmp_path, capsys, args, message):
    missing = tmp_path / "missing"

    assert _run([str(missing), *args]) == 1

    captured = capsys.readouterr()
    # Validation runs before the path is resolved.
    assert captured.err.strip() == message
    assert captured.out == ""


def test_validate_accepts_zero_and_inf():
    options = {"warn": 0.0, "error": float("inf"), "critical": 0.0, "top": 0, "image": None}

    assert CheckRubycritic._validate(options) is options


def test_apply_defaults_fills_unset_values():
    cli = {"path": "x", "warn": None, "error": 5.0, "critical": None, "top": None,
           "min_level": None, "fail_on": None, "image": None}

    options = CheckRubycritic._apply_defaults(cli)

    assert options == {"path": "x", "warn": 100, "error": 5.0, "critical": 400, "top": 0,
                       "min_level": "ok", "fail_on": None, "image": None}


# --- path resolution ---------------------------------------------------------------


def test_run_path_not_found_exits_one(tmp_path, capsys):
    missing = tmp_path / "missing"

    assert _run([str(missing), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == f"Error: path not found: {missing.resolve()}"


def test_resolve_target_directory_is_its_own_root(tmp_path):
    target, root = CheckRubycritic._resolve_target(str(tmp_path))

    assert target == tmp_path.resolve()
    assert root == tmp_path.resolve()


def test_resolve_target_file_root_is_parent(tmp_path):
    file_path = tmp_path / "a.rb"
    file_path.write_text("x\n")

    target, root = CheckRubycritic._resolve_target(str(file_path))

    assert target == file_path.resolve()
    assert root == tmp_path.resolve()


def test_resolve_target_unreadable_file(tmp_path, monkeypatch):
    file_path = tmp_path / "a.rb"
    file_path.write_text("x\n")
    modes = []

    def fake_access(path, mode):
        modes.append(mode)
        return False

    monkeypatch.setattr(os, "access", fake_access)

    with pytest.raises(RubycriticError) as exc_info:
        CheckRubycritic._resolve_target(str(file_path))

    assert exc_info.value.message == f"path not readable: {file_path.resolve()}"
    assert modes == [os.R_OK]


def test_resolve_target_directory_needs_read_and_execute(tmp_path, monkeypatch):
    modes = []

    def fake_access(path, mode):
        modes.append(mode)
        return mode == os.R_OK

    monkeypatch.setattr(os, "access", fake_access)

    with pytest.raises(RubycriticError, match="path not readable"):
        CheckRubycritic._resolve_target(str(tmp_path))

    assert modes == [os.R_OK | os.X_OK]


def test_run_unreadable_path_exits_one(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(os, "access", lambda path, mode: False)

    assert _run([str(tmp_path), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == f"Error: path not readable: {tmp_path.resolve()}"


def test_resolve_target_colon_in_directory_root(tmp_path):
    target = tmp_path / "a:b"
    target.mkdir()

    with pytest.raises(RubycriticError) as exc_info:
        CheckRubycritic._resolve_target(str(target))

    assert exc_info.value.message == (
        f"cannot mount {target.resolve()}: Docker volume paths cannot contain ':'"
    )


def test_resolve_target_colon_in_file_parent(tmp_path):
    parent = tmp_path / "a:b"
    parent.mkdir()
    (parent / "x.rb").write_text("x\n")

    with pytest.raises(RubycriticError, match=r"cannot mount .*a:b: Docker volume"):
        CheckRubycritic._resolve_target(str(parent / "x.rb"))


def test_resolve_target_colon_in_file_name_only_is_fine(tmp_path):
    file_path = tmp_path / "a:b.rb"
    file_path.write_text("x\n")

    _target, root = CheckRubycritic._resolve_target(str(file_path))

    assert root == tmp_path.resolve()


# --- image ------------------------------------------------------------------------


def test_run_unreadable_version_file_exits_one(tmp_path, capsys, monkeypatch):
    from code_check.rubycritic.constants import Constants

    missing = tmp_path / "VERSION"
    monkeypatch.setattr(Constants, "VERSION_FILE", missing)

    assert _run([str(tmp_path)]) == 1

    assert capsys.readouterr().err.strip() == (
        f"Error: cannot read the tingle version from {missing}; use --image to choose the image"
    )


# --- header -----------------------------------------------------------------------


def test_print_header(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    options = {"warn": 100, "error": 12.5, "critical": 400.0}

    CheckRubycritic._print_header(Palette(), tmp_path, options, "img:1")

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\n"
        "Thresholds: warn=100 | error=12.5 | critical=400\n"
        "Image: img:1\n"
        "\n"
    )
