"""Unit tests for code_check.file_size.reporter.Reporter."""

from __future__ import annotations

import io
from pathlib import Path

from code_check.file_size.constants import Constants
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.file_size.palette import Palette
from code_check.file_size.reporter import Reporter


class FakeTTY(io.StringIO):
    """In-memory stream that reports itself as a TTY."""

    def isatty(self) -> bool:
        return True


def test_report_mixed_results_prints_row_per_result_and_summary(tmp_path, capsys):
    target = tmp_path
    ok_file = target / "ok.py"
    ok_file.write_text("a\n")
    warn_file = target / "warn.py"
    warn_file.write_text("a\n")
    error_file = target / "error.py"
    error_file.write_text("a\n")

    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    results = [
        (ok_file, 10),
        (ok_file, 20),
        (warn_file, 300),
        (error_file, 500),
    ]

    Reporter(analyzer, target).report(results)

    out = capsys.readouterr().out

    assert out.count("✅ OK") == 2
    assert out.count("⚠️  WARN") == 1
    assert out.count("🔴 ERROR") == 1
    assert "2 OK" in out
    assert "1 WARN" in out
    assert "1 ERROR" in out
    assert "0 CRITICAL" in out
    assert "Total:" in out
    assert FileAnalyzer.format_number(830) in out


def test_report_empty_results_prints_headers_and_zeroed_summary(tmp_path, capsys):
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)

    Reporter(analyzer, tmp_path).report([])

    out = capsys.readouterr().out

    assert "Status" in out
    assert "0 file(s)" in out
    assert "0 OK" in out
    assert "0 WARN" in out
    assert "0 ERROR" in out
    assert "0 CRITICAL" in out
    assert "Total:" in out
    assert "0 lines" in out


def test_report_display_path_relative_to_target_parent_when_directory(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    nested = target / "sub" / "file.py"
    nested.parent.mkdir()
    nested.write_text("a\n")

    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    Reporter(analyzer, target).report([(nested, 1)])

    out = capsys.readouterr().out

    expected = str(nested.relative_to(target.parent))
    assert expected in out


def test_report_display_path_is_name_only_when_target_is_a_file(tmp_path, capsys):
    target = tmp_path / "single.py"
    target.write_text("a\n")

    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    Reporter(analyzer, target).report([(target, 1)])

    out = capsys.readouterr().out

    assert target.name in out
    assert str(target) not in out


def test_report_display_path_falls_back_to_str_on_value_error(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    unrelated = Path("/completely/unrelated/path.py")

    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    Reporter(analyzer, target).report([(unrelated, 1)])

    out = capsys.readouterr().out

    assert str(unrelated) in out


def test_report_is_plain_text_when_stdout_is_not_a_tty(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)

    Reporter(analyzer, tmp_path).report([(tmp_path / "a.py", 1000)])

    out = capsys.readouterr().out
    assert "\033[" not in out
    assert "🟣 CRITICAL" in out


def test_report_is_plain_text_when_no_color_is_set(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)

    Reporter(analyzer, tmp_path, Palette(FakeTTY())).report([(tmp_path / "a.py", 1)])

    out = capsys.readouterr().out
    assert "\033[" not in out
    assert "✅ OK" in out


def test_report_is_coloured_with_a_tty_palette(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)

    Reporter(analyzer, tmp_path, Palette(FakeTTY())).report([(tmp_path / "a.py", 500)])

    out = capsys.readouterr().out
    assert f"{Constants.RED}{Constants.BOLD}🔴 ERROR" in out
    assert f"{Constants.BOLD}Summary:{Constants.RESET}" in out


def test_report_summary_uses_full_results_when_fewer_rows_are_shown(tmp_path, capsys):
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    big = tmp_path / "big.py"
    small = tmp_path / "small.py"
    results = [(big, 1000), (small, 10)]

    Reporter(analyzer, tmp_path).report(results, [(big, 1000)], "critical")

    out = capsys.readouterr().out
    assert "big.py" in out
    assert "small.py" not in out
    assert "2 file(s)" in out
    assert "1 OK" in out
    assert "1 CRITICAL" in out
    assert f"Total: {FileAnalyzer.format_number(1010)} lines" in out


def test_report_empty_shown_prints_note_and_no_table_header(tmp_path, capsys):
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    results = [(tmp_path / "a.py", 10)]

    Reporter(analyzer, tmp_path).report(results, [], "warn")

    out = capsys.readouterr().out
    assert out.startswith("No files at or above WARN.\n\n")
    assert "Status" not in out
    assert "Lines" not in out
    assert "a.py" not in out
    assert "1 file(s)" in out
    assert "1 OK" in out
    assert "Total: 10 lines" in out


def test_report_shown_none_keeps_current_output(tmp_path, capsys):
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)
    results = [(tmp_path / "a.py", 500), (tmp_path / "b.py", 10)]

    Reporter(analyzer, tmp_path).report(results)
    default_out = capsys.readouterr().out

    Reporter(analyzer, tmp_path).report(results, results, "ok")
    explicit_out = capsys.readouterr().out

    assert default_out == explicit_out
    assert "Status" in default_out
    assert "a.py" in default_out
    assert "b.py" in default_out
