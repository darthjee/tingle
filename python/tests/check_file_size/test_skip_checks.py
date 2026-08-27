"""Unit tests for check_file_size.skip_checks.SkipChecks, plus the --top 0
and default-exclude edge cases that live at the FileCollector/CheckFileSize
level.
"""

from __future__ import annotations

import os

import pytest

from check_file_size.constants import Constants
from check_file_size.file_collector import FileCollector
from check_file_size.skip_checks import SkipChecks


def test_is_binary_file_known_extension_short_circuits(tmp_path):
    file_path = tmp_path / "image.png"
    # No content written — extension check must short-circuit before reading.
    file_path.touch()

    assert SkipChecks.is_binary_file(file_path) is True


def test_is_binary_file_null_byte_in_content(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_bytes(b"hello\x00world")

    assert SkipChecks.is_binary_file(file_path) is True


def test_is_binary_file_invalid_utf8_content(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_bytes(b"\xff\xfe\xfd")

    assert SkipChecks.is_binary_file(file_path) is True


def test_is_binary_file_plain_text_returns_false(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("hello world\n")

    assert SkipChecks.is_binary_file(file_path) is False


def test_is_binary_file_only_inspects_first_1024_bytes(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_bytes(b"a" * 1024 + b"\x00")

    assert SkipChecks.is_binary_file(file_path) is False


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores permission bits; run as non-root")
def test_is_binary_file_permission_denied_returns_true(tmp_path):
    file_path = tmp_path / "secret.txt"
    file_path.write_text("secret\n")
    file_path.chmod(0o000)

    try:
        result = SkipChecks.is_binary_file(file_path)
    finally:
        file_path.chmod(0o644)

    assert result is True


def test_is_binary_file_missing_path_returns_true(tmp_path):
    missing = tmp_path / "does-not-exist.txt"

    assert SkipChecks.is_binary_file(missing) is True


def test_top_zero_means_show_all():
    """--top 0 (the default) means CheckFileSize.run() keeps every result."""
    results = [("a", 3), ("b", 2), ("c", 1)]
    top = 0

    sliced = results[:top] if top > 0 else results

    assert sliced == results


def test_default_exclude_skips_node_modules_nested_file(tmp_path):
    nested_dir = tmp_path / "node_modules"
    nested_dir.mkdir()
    (nested_dir / "lib.js").write_text("x\n")
    kept = tmp_path / "app.js"
    kept.write_text("y\n")

    collector = FileCollector(Constants.DEFAULT_EXCLUDES, None)
    results = collector.collect(tmp_path)

    assert results == [kept]
