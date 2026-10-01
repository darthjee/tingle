"""Unit tests for code_check.rubycritic.selection."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.rubycritic.selection import (
    Selection,
    build_selection,
    select_files,
    unsendable_reason,
)

NON_UTF8 = b"bad\xff.rb".decode("utf-8", "surrogateescape")


def _touch(root, *rel_paths, content="x = 1\n"):
    for rel in rel_paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


# --- directory mode ----------------------------------------------------------------


def test_directory_lines_are_sorted_posix_and_relative(tmp_path):
    _touch(tmp_path, "z.rb", "lib/b.rb", "lib/a.rb", "app/models/user.rb", "README.md")

    selection = select_files(tmp_path, tmp_path)

    assert selection == Selection(
        tmp_path, ["app/models/user.rb", "lib/a.rb", "lib/b.rb", "z.rb"], []
    )


def test_directory_uppercase_extension_is_selected(tmp_path):
    _touch(tmp_path, "Upper.RB", "lower.rb", "other.py")

    assert select_files(tmp_path, tmp_path).lines == ["Upper.RB", "lower.rb"]


@pytest.mark.parametrize("excluded", ["tmp", "log", ".bundle", "vendor", "node_modules", "Tmp"])
def test_directory_default_excludes(tmp_path, excluded):
    _touch(tmp_path, f"{excluded}/skip.rb", "keep.rb")

    assert select_files(tmp_path, tmp_path).lines == ["keep.rb"]


def test_directory_keeps_non_utf8_content(tmp_path):
    (tmp_path / "bad.rb").write_bytes(b"puts '\xff'\n\x00")

    assert select_files(tmp_path, tmp_path).lines == ["bad.rb"]


def test_directory_gitignore_is_not_applied(tmp_path, monkeypatch):
    from code_check.file_size.git_ignore import GitIgnore

    def boom(root):
        raise AssertionError("git must not be called")

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(boom))
    _touch(tmp_path, "a.rb")

    assert select_files(tmp_path, tmp_path).lines == ["a.rb"]


def test_empty_directory_selects_nothing(tmp_path):
    assert select_files(tmp_path, tmp_path) == Selection(tmp_path, [], [])


# --- single-file mode --------------------------------------------------------------


def test_single_file_sends_only_its_name(tmp_path):
    _touch(tmp_path, "a.rb", "b.rb")

    selection = select_files(tmp_path / "a.rb", tmp_path)

    assert selection.root == tmp_path
    assert selection.lines == ["a.rb"]


def test_single_file_inside_excluded_dir_is_kept(tmp_path):
    _touch(tmp_path, "tmp/a.rb")

    assert select_files(tmp_path / "tmp" / "a.rb", tmp_path / "tmp").lines == ["a.rb"]


def test_single_non_ruby_file_selects_nothing(tmp_path):
    _touch(tmp_path, "a.py")

    assert select_files(tmp_path / "a.py", tmp_path).lines == []


# --- unsendable names --------------------------------------------------------------


def test_unsendable_reason_plain_names_are_fine():
    assert unsendable_reason("dir with space/tab\tname é.rb") is None


def test_unsendable_reason_newline():
    assert unsendable_reason("a\nb.rb") == (
        "skipping file with a newline in its name: 'a\\nb.rb'"
    )


def test_unsendable_reason_non_utf8():
    assert unsendable_reason(NON_UTF8) == (
        f"skipping file whose name is not valid UTF-8: {NON_UTF8!r}"
    )


def test_build_selection_drops_unsendable_names():
    root = Path("/project")
    files = [root / "b.rb", root / "a\nb.rb", root / "lib" / NON_UTF8, root / "a.rb"]

    selection = build_selection(root, files)

    assert selection.lines == ["a.rb", "b.rb"]
    assert selection.skipped == [
        "skipping file with a newline in its name: 'a\\nb.rb'",
        f"skipping file whose name is not valid UTF-8: {'lib/' + NON_UTF8!r}",
    ]
