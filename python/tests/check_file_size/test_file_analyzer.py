"""Unit tests for check_file_size.file_analyzer.FileAnalyzer."""

from __future__ import annotations

import os

import pytest

from check_file_size.file_analyzer import FileAnalyzer


def test_count_lines_returns_exact_count(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line1\nline2\nline3\n")

    assert FileAnalyzer.count_lines(file_path) == 3


def test_count_lines_no_trailing_newline(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line1\nline2")

    assert FileAnalyzer.count_lines(file_path) == 2


def test_count_lines_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("")

    assert FileAnalyzer.count_lines(file_path) == 0


def test_count_lines_missing_path_returns_minus_one(tmp_path):
    missing = tmp_path / "does-not-exist.txt"

    assert FileAnalyzer.count_lines(missing) == -1


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores permission bits; run as non-root")
def test_count_lines_permission_denied_returns_minus_one(tmp_path):
    file_path = tmp_path / "secret.txt"
    file_path.write_text("secret\n")
    file_path.chmod(0o000)

    try:
        result = FileAnalyzer.count_lines(file_path)
    finally:
        file_path.chmod(0o644)

    assert result == -1


@pytest.mark.parametrize(
    "lines, expected_label, expected_level",
    [
        (1000, "🟣 CRITICAL", "critical"),
        (999, "🔴 ERROR", "error"),
        (500, "🔴 ERROR", "error"),
        (499, "⚠️  WARN", "warn"),
        (300, "⚠️  WARN", "warn"),
        (299, "✅ OK", "ok"),
        (0, "✅ OK", "ok"),
    ],
)
def test_classify_boundaries(lines, expected_label, expected_level):
    analyzer = FileAnalyzer(warn=300, error=500, critical=1000)

    label, level = analyzer.classify(lines)

    assert label == expected_label
    assert level == expected_level


def test_format_number_uses_dot_thousands_separator():
    assert FileAnalyzer.format_number(1234) == "1.234"
    assert FileAnalyzer.format_number(1234567) == "1.234.567"
    assert FileAnalyzer.format_number(0) == "0"
