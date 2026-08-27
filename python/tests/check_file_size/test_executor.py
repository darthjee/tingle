"""Unit tests for check_file_size.executor.CheckFileSize."""

from __future__ import annotations

import pytest

from check_file_size.executor import CheckFileSize


def test_run_no_args_prints_help_and_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([])

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_run_path_not_found_prints_error_and_exits_one(tmp_path, capsys):
    missing = tmp_path / "does_not_exist"

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(missing)])

    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "Error: path not found" in out


def test_run_no_files_found_prints_message_and_exits_zero(tmp_path, capsys):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(empty_dir)])

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "No files found for analysis." in out


def test_run_analyzes_and_reports_files(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    (target / "small.py").write_text("a\n")
    (target / "big.py").write_text("\n".join(str(i) for i in range(600)))

    CheckFileSize().run([str(target)])

    out = capsys.readouterr().out
    assert "Analyzing:" in out
    assert "small.py" in out
    assert "big.py" in out
    assert "Total:" in out


def test_run_applies_top_flag_to_limit_results(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    (target / "a.py").write_text("1\n" * 10)
    (target / "b.py").write_text("1\n" * 20)

    CheckFileSize().run([str(target), "--top", "1"])

    out = capsys.readouterr().out
    assert "b.py" in out
    assert "a.py" not in out
