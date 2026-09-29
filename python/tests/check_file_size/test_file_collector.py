"""Unit tests for check_file_size.file_collector.FileCollector."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from check_file_size.file_collector import FileCollector
from check_file_size.git_ignore import GitIgnore, GitIgnored


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


def _make_tree(root, *rel_paths):
    for rel in rel_paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")


def _rel(root, paths):
    return {p.relative_to(root).as_posix() for p in paths}


def test_collect_ignore_drops_unanchored_matches(tmp_path):
    _make_tree(tmp_path, "a.test.js", "src/b.TEST.js", "src/c.js")

    collector = FileCollector([], None, ignore=["*.test.js"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"src/c.js"}


def test_collect_ignore_anchored_pattern(tmp_path):
    _make_tree(tmp_path, "tests/fixtures/a.json", "tests/fixtures/x/b.json",
               "lib/tests/fixtures/c.json", "tests/test_a.py")

    collector = FileCollector([], None, ignore=["tests/fixtures/**"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {
        "lib/tests/fixtures/c.json", "tests/test_a.py",
    }


def test_collect_ignore_is_repeatable(tmp_path):
    _make_tree(tmp_path, "docs/guide.txt", "README.md", "src/a.py")

    collector = FileCollector([], None, ignore=["docs/**", "*.md"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"src/a.py"}


def test_collect_include_keeps_only_matches(tmp_path):
    _make_tree(tmp_path, "src/a.py", "src/x/b.js", "lib/c.py", "d.py")

    collector = FileCollector([], None, include=["src/**"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"src/a.py", "src/x/b.js"}


def test_collect_empty_include_list_keeps_everything(tmp_path):
    _make_tree(tmp_path, "a.py", "b.js")

    collector = FileCollector([], None, include=[""])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"a.py", "b.js"}


def test_collect_include_and_ext_are_combined_with_and(tmp_path):
    _make_tree(tmp_path, "src/a.py", "src/b.js", "lib/c.py")

    collector = FileCollector([], [".py"], include=["src/**"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"src/a.py"}


def test_collect_ignore_wins_over_include(tmp_path):
    _make_tree(tmp_path, "src/a.py", "src/vendor/b.py", "lib/c.py")

    collector = FileCollector([], None, include=["src/**"], ignore=["src/vendor/"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"src/a.py"}


def test_collect_globs_still_skip_binary_files(tmp_path):
    _make_tree(tmp_path, "src/a.py")
    (tmp_path / "src" / "b.png").write_bytes(b"\x00\x01")

    collector = FileCollector([], None, include=["src/**"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"src/a.py"}


def test_collect_single_file_ignore_matches_on_name(tmp_path):
    file_path = tmp_path / "main.py"
    file_path.write_text("x\n")

    assert FileCollector([], None, ignore=["main.*"]).collect(file_path) == []
    assert FileCollector([], None, ignore=["other.*"]).collect(file_path) == [file_path]


def test_collect_single_file_include_matches_on_name(tmp_path):
    file_path = tmp_path / "main.py"
    file_path.write_text("x\n")

    assert FileCollector([], None, include=["*.py"]).collect(file_path) == [file_path]
    assert FileCollector([], None, include=["*.js"]).collect(file_path) == []


def test_collect_exclude_ignores_components_above_target(tmp_path):
    target = tmp_path / "build" / "proj"
    _make_tree(target, "a.py", "src/b.py")

    collector = FileCollector(["build"], None)

    assert _rel(target, collector.collect(target)) == {"a.py", "src/b.py"}


def test_collect_exclude_matches_whole_components_only(tmp_path):
    _make_tree(tmp_path, "build/x.js", "a/build/y.js", "builder/z.js", "a/rebuild.js")

    collector = FileCollector(["build"], None)

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"builder/z.js", "a/rebuild.js"}


def test_collect_exclude_is_case_insensitive_both_ways(tmp_path):
    _make_tree(tmp_path, "Build/x.js", "a/BUILD/y.js", "keep.js")

    assert _rel(tmp_path, FileCollector(["build"], None).collect(tmp_path)) == {"keep.js"}
    assert _rel(tmp_path, FileCollector(["BuIlD"], None).collect(tmp_path)) == {"keep.js"}


def test_collect_single_file_inside_excluded_dir_is_returned(tmp_path):
    _make_tree(tmp_path, "node_modules/pkg/index.js")
    file_path = tmp_path / "node_modules" / "pkg" / "index.js"

    collector = FileCollector(["node_modules"], None)

    assert collector.collect(file_path) == [file_path]


@pytest.fixture
def fake_git(monkeypatch):
    """Mock GitIgnore.ignored_paths; returns the list of roots it was called with."""
    state = {"calls": [], "result": None}

    def ignored_paths(root):
        state["calls"].append(root)
        return state["result"]

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(ignored_paths))
    return state


def test_collect_gitignore_drops_ignored_files_and_directories(tmp_path, fake_git):
    _make_tree(tmp_path, "main.py", "debug.log", "dist/app.js", "dist/x/y.js")
    root = tmp_path.resolve()
    fake_git["result"] = GitIgnored({root / "debug.log"}, [root / "dist"])

    results = FileCollector([], None).collect(tmp_path)

    assert _rel(tmp_path, results) == {"main.py"}
    assert fake_git["calls"] == [root]


def test_collect_gitignore_disabled_keeps_files_and_skips_git(tmp_path, fake_git):
    _make_tree(tmp_path, "main.py", "debug.log", "dist/app.js")
    root = tmp_path.resolve()
    fake_git["result"] = GitIgnored({root / "debug.log"}, [root / "dist"])

    results = FileCollector([], None, gitignore=False).collect(tmp_path)

    assert _rel(tmp_path, results) == {"main.py", "debug.log", "dist/app.js"}
    assert fake_git["calls"] == []


def test_collect_gitignore_none_drops_nothing(tmp_path, fake_git):
    _make_tree(tmp_path, "main.py", "debug.log")

    results = FileCollector([], None).collect(tmp_path)

    assert _rel(tmp_path, results) == {"main.py", "debug.log"}
    assert len(fake_git["calls"]) == 1


def test_collect_gitignore_single_file_uses_parent(tmp_path, fake_git):
    _make_tree(tmp_path, "debug.log", "main.py")
    root = tmp_path.resolve()
    fake_git["result"] = GitIgnored({root / "debug.log"}, [])

    assert FileCollector([], None).collect(tmp_path / "debug.log") == []
    assert FileCollector([], None).collect(tmp_path / "main.py") == [tmp_path / "main.py"]
    assert fake_git["calls"] == [root, root]


def test_collect_gitignore_single_file_disabled(tmp_path, fake_git):
    _make_tree(tmp_path, "debug.log")
    fake_git["result"] = GitIgnored({tmp_path.resolve() / "debug.log"}, [])

    collector = FileCollector([], None, gitignore=False)

    assert collector.collect(tmp_path / "debug.log") == [tmp_path / "debug.log"]
    assert fake_git["calls"] == []


def test_collect_gitignore_called_once_per_collect(tmp_path, fake_git):
    _make_tree(tmp_path, "a.py", "b.py", "sub/c.py", "sub/d.py")

    collector = FileCollector([], None)
    collector.collect(tmp_path)
    collector.collect(tmp_path)

    assert len(fake_git["calls"]) == 2


def test_collect_gitignore_runs_after_excludes_and_before_globs(tmp_path, fake_git):
    _make_tree(tmp_path, "keep.py", "gen.py", "vendor/lib.py")
    root = tmp_path.resolve()
    fake_git["result"] = GitIgnored({root / "gen.py"}, [])

    collector = FileCollector(["vendor"], None, include=["*.py"])

    assert _rel(tmp_path, collector.collect(tmp_path)) == {"keep.py"}


def test_collect_gitignore_relative_target(tmp_path, fake_git, monkeypatch):
    _make_tree(tmp_path, "main.py", "debug.log")
    fake_git["result"] = GitIgnored({tmp_path.resolve() / "debug.log"}, [])
    monkeypatch.chdir(tmp_path)

    results = FileCollector([], None).collect(Path("."))

    assert {p.as_posix() for p in results} == {"main.py"}
    assert fake_git["calls"] == [tmp_path.resolve()]
