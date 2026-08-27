"""Unit tests for check_file_size.file_collector.FileCollector."""

from __future__ import annotations

import os

import pytest

from check_file_size.file_collector import FileCollector


def test_collect_single_file_not_binary_returns_it(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("print('hi')\n")

    collector = FileCollector([], None)

    assert collector.collect(file_path) == [file_path]


def test_collect_single_file_binary_returns_empty(tmp_path):
    file_path = tmp_path / "image.png"
    file_path.write_bytes(b"\x00\x01\x02")

    collector = FileCollector([], None)

    assert collector.collect(file_path) == []


def test_collect_directory_recurses_and_skips_directories(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.py").write_text("a\n")
    (tmp_path / "b.py").write_text("b\n")

    collector = FileCollector([], None)
    results = collector.collect(tmp_path)

    assert set(results) == {tmp_path / "sub" / "a.py", tmp_path / "b.py"}
    assert all(p.is_file() for p in results)


def test_collect_excludes_directory_component_case_insensitive(tmp_path):
    (tmp_path / "Node_Modules").mkdir()
    (tmp_path / "Node_Modules" / "lib.js").write_text("x\n")
    (tmp_path / "app.js").write_text("y\n")

    collector = FileCollector(["node_modules"], None)
    results = collector.collect(tmp_path)

    assert results == [tmp_path / "app.js"]


def test_collect_filters_by_extension_case_insensitive(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    (tmp_path / "b.JS").write_text("b\n")
    (tmp_path / "c.txt").write_text("c\n")

    collector = FileCollector([], [".py", ".js"])
    results = collector.collect(tmp_path)

    assert set(results) == {tmp_path / "a.py", tmp_path / "b.JS"}


def test_collect_no_extension_filter_when_none_passed(tmp_path):
    (tmp_path / "a.py").write_text("a\n")
    (tmp_path / "b.txt").write_text("b\n")

    collector = FileCollector([], None)
    results = collector.collect(tmp_path)

    assert set(results) == {tmp_path / "a.py", tmp_path / "b.txt"}


def test_collect_excludes_binary_files_in_directory(tmp_path):
    (tmp_path / "keep.py").write_text("a\n")
    (tmp_path / "skip.png").write_bytes(b"\x00\x01")

    collector = FileCollector([], None)
    results = collector.collect(tmp_path)

    assert results == [tmp_path / "keep.py"]


def test_collect_empty_directory_returns_empty_list(tmp_path):
    collector = FileCollector([], None)

    assert collector.collect(tmp_path) == []


def test_collect_nonexistent_path_returns_empty_list(tmp_path):
    missing = tmp_path / "does-not-exist"
    collector = FileCollector([], None)

    assert collector.collect(missing) == []


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores permission bits; run as non-root")
def test_collect_skips_permission_denied_subdirectory(tmp_path):
    denied = tmp_path / "denied"
    denied.mkdir()
    (denied / "secret.py").write_text("secret\n")
    (tmp_path / "visible.py").write_text("visible\n")

    denied.chmod(0o000)
    try:
        collector = FileCollector([], None)
        results = collector.collect(tmp_path)
    finally:
        denied.chmod(0o755)

    assert results == [tmp_path / "visible.py"]
