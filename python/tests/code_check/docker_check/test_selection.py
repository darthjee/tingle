"""Unit tests for code_check.docker_check.selection."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.docker_check.selection import (
    Selection,
    build_selection,
    select_files,
    unsendable_reason,
)
from code_check.file_size.git_ignore import GitIgnore

EXTENSIONS = [".js", ".ts"]
EXCLUDES = ["node_modules"]


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths (no real git)."""
    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(lambda root: None))


def _touch(root, *rel_paths):
    for rel in rel_paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")


def _select(target, root, **kwargs):
    kwargs.setdefault("extensions", EXTENSIONS)
    kwargs.setdefault("excludes", EXCLUDES)
    return select_files(target, root, **kwargs)


def test_other_extensions_are_selected(tmp_path):
    _touch(tmp_path, "b.ts", "a.js", "c.rb", "lib/d.JS", "node_modules/e.js")

    assert _select(tmp_path, tmp_path) == Selection(tmp_path, ["a.js", "b.ts", "lib/d.JS"], [])


def test_single_file_target(tmp_path):
    _touch(tmp_path, "a.js")

    assert _select(tmp_path / "a.js", tmp_path).lines == ["a.js"]


def test_ignore_and_include_globs(tmp_path):
    _touch(tmp_path, "src/a.js", "src/b.js", "test/c.js")

    assert _select(tmp_path, tmp_path, include=["src/**"], ignore=["src/b.js"]).lines == [
        "src/a.js"
    ]


def test_skip_none_matches_default(tmp_path):
    _touch(tmp_path, "a.js", "a.min.js")

    assert _select(tmp_path, tmp_path, skip=None) == _select(tmp_path, tmp_path)
    assert _select(tmp_path, tmp_path).lines == ["a.js", "a.min.js"]


def test_skip_drops_plain_file_silently(tmp_path):
    _touch(tmp_path, "a.js", "a.min.js", "types.d.ts")
    seen = []

    def skip(path):
        seen.append(path)
        return path.name.endswith((".min.js", ".d.ts"))

    selection = _select(tmp_path, tmp_path, skip=skip)

    assert selection == Selection(tmp_path, ["a.js"], [])
    assert sorted(p.name for p in seen) == ["a.js", "a.min.js", "types.d.ts"]


def test_skip_is_called_on_the_walked_symlink_path(tmp_path):
    _touch(tmp_path, "real/target.js")
    link = tmp_path / "link.min.js"
    link.symlink_to(tmp_path / "real" / "target.js")
    seen = []

    def skip(path):
        seen.append(path)
        return path.name.endswith(".min.js")

    selection = _select(tmp_path, tmp_path, skip=skip)

    assert selection.lines == ["real/target.js"]
    assert link in seen


def test_skip_on_symlink_drops_the_link_but_not_the_target(tmp_path):
    _touch(tmp_path, "real/target.min.js")
    (tmp_path / "plain.js").symlink_to(tmp_path / "real" / "target.min.js")

    selection = _select(
        tmp_path, tmp_path, skip=lambda path: path.name == "plain.js"
    )

    assert selection.lines == ["real/target.min.js"]


def test_symlink_outside_root_is_dropped(tmp_path):
    inside = tmp_path / "inside"
    outside = tmp_path / "outside"
    _touch(outside, "secret.js")
    _touch(inside, "a.js")
    (inside / "link.js").symlink_to(outside / "secret.js")

    assert _select(inside, inside).lines == ["a.js"]


def test_unsendable_names_are_reported():
    assert unsendable_reason("ok.js") is None
    assert unsendable_reason("a\nb.js") == "skipping file with a newline in its name: 'a\\nb.js'"
    bad = b"bad\xff.js".decode("utf-8", "surrogateescape")
    assert unsendable_reason(bad) == f"skipping file whose name is not valid UTF-8: {bad!r}"


def test_build_selection_dedups_and_sorts(tmp_path):
    _touch(tmp_path, "b.js", "a.js")
    files = [tmp_path / "b.js", tmp_path / "a.js", tmp_path / "." / "a.js"]

    assert build_selection(tmp_path, files) == Selection(tmp_path, ["a.js", "b.js"], [])


def test_build_selection_records_skipped(tmp_path):
    name = "a\nb.js"
    (tmp_path / name).write_text("x")

    selection = build_selection(tmp_path, [Path(tmp_path / name)])

    assert selection.lines == []
    assert selection.skipped == [unsendable_reason(name)]
