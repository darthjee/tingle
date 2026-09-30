"""Unit tests for code_check.executor.CodeCheck (subcommand dispatch)."""

from __future__ import annotations

import io

import pytest

from code_check.executor import CodeCheck
from code_check.file_size.executor import CheckFileSize
from code_check.palette import Colors

LIST_FOOTER = "Run 'tingle code_check <subcommand> --help' for its options."


class FakeTTY(io.StringIO):
    """In-memory stream that reports itself as a TTY."""

    def isatty(self) -> bool:
        return True


@pytest.fixture
def spy(monkeypatch):
    """Replace the file_size class in SUBCOMMANDS with a recorder."""
    calls: list[list[str]] = []

    class FakeFileSize:
        def run(self, args):
            calls.append(args)

    monkeypatch.setitem(CodeCheck.SUBCOMMANDS, "file_size", (FakeFileSize, "desc"))
    return calls


def _run(args):
    with pytest.raises(SystemExit) as exc_info:
        CodeCheck().run(args)
    return exc_info.value.code


# --- subcommand table -----------------------------------------------------------


def test_subcommands_maps_file_size_to_executor():
    cls, description = CodeCheck.SUBCOMMANDS["file_size"]

    assert cls is CheckFileSize
    assert description


# --- listing --------------------------------------------------------------------


@pytest.mark.parametrize("args", [[], ["-h"], ["--help"]])
def test_list_on_no_args_or_help_exits_zero(capsys, args):
    assert _run(args) == 0

    captured = capsys.readouterr()
    assert "file_size" in captured.out
    assert "Token efficiency triage: file size analysis." in captured.out
    assert captured.out.rstrip().endswith(LIST_FOOTER)
    assert captured.err == ""


# --- dispatch -------------------------------------------------------------------


def test_dispatches_subcommand_with_remaining_args(spy):
    CodeCheck().run(["file_size", ".", "--warn", "100"])

    assert spy == [[".", "--warn", "100"]]


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_before_subcommand_is_forwarded_as_subcommand_help(spy, flag):
    CodeCheck().run([flag, "file_size", "--top", "3"])

    assert spy == [[flag, "--top", "3"]]


@pytest.mark.parametrize("args", [["-h", "file_size"], ["--help", "file_size"], ["file_size", "-h"]])
def test_file_size_help_is_printed_and_exits_zero(capsys, args):
    assert _run(args) == 0

    assert capsys.readouterr().out.startswith("usage: tingle code_check file_size ")


def test_file_size_without_path_prints_its_help_and_exits_zero(capsys):
    assert _run(["file_size"]) == 0

    assert capsys.readouterr().out.startswith("usage: tingle code_check file_size ")


# --- errors ---------------------------------------------------------------------


def test_flag_before_subcommand_exits_one(capsys, spy):
    assert _run(["--warn", "100", "file_size", "."]) == 1

    captured = capsys.readouterr()
    assert "Error: expected a subcommand before options (got '--warn')" in captured.err
    assert "file_size" in captured.err
    assert LIST_FOOTER in captured.err
    assert captured.out == ""
    assert spy == []


@pytest.mark.parametrize("name", ["File_Size", "file-size", "nope"])
def test_unknown_subcommand_exits_one(capsys, spy, name):
    assert _run([name, "."]) == 1

    captured = capsys.readouterr()
    assert f"Error: unknown subcommand '{name}'" in captured.err
    assert LIST_FOOTER in captured.err
    assert captured.out == ""
    assert spy == []


def test_unknown_name_after_help_is_an_unknown_subcommand(capsys):
    assert _run(["-h", "nope"]) == 1

    assert "Error: unknown subcommand 'nope'" in capsys.readouterr().err


def test_error_is_plain_when_stderr_is_not_a_tty(capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    _run(["nope"])

    assert Colors.RED not in capsys.readouterr().err


def test_error_is_red_when_stderr_is_a_tty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    stderr = FakeTTY()
    monkeypatch.setattr("sys.stderr", stderr)

    _run(["nope"])

    assert f"{Colors.RED}Error: unknown subcommand 'nope'{Colors.RESET}" in stderr.getvalue()


# --- exit codes forwarded -------------------------------------------------------


def test_file_size_success_exit_code_is_forwarded(tmp_path, capsys):
    (tmp_path / "a.py").write_text("1\n")

    CodeCheck().run(["file_size", str(tmp_path), "--no-config"])

    assert "a.py" in capsys.readouterr().out


def test_file_size_error_exit_code_is_forwarded(tmp_path, capsys):
    assert _run(["file_size", str(tmp_path / "missing")]) == 1


def test_file_size_usage_error_exit_code_is_forwarded(tmp_path, capsys):
    assert _run(["file_size", str(tmp_path), "--warn", "x"]) == 1


def test_file_size_fail_on_exit_code_is_forwarded(tmp_path, capsys):
    (tmp_path / "big.py").write_text("1\n" * 20)

    assert _run(["file_size", str(tmp_path), "--no-config", "--warn", "5", "--fail-on", "warn"]) == 2
