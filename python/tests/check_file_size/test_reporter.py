"""Unit tests for check_file_size.reporter.Reporter."""

from __future__ import annotations

from pathlib import Path

from check_file_size.file_analyzer import FileAnalyzer
from check_file_size.reporter import Reporter


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
