"""Unit tests for code_check.js_complexity.selection."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.js_complexity.constants import Constants
from code_check.js_complexity.selection import (
    Selection,
    build_selection,
    is_declaration,
    select_files,
    unsendable_reason,
)

NON_UTF8 = b"bad\xff.js".decode("utf-8", "surrogateescape")


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths (no real git); returns the roots it was called with."""
    state = {"calls": [], "result": None}

    def ignored_paths(root):
        state["calls"].append(root)
        return state["result"]

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(ignored_paths))
    return state


def _touch(root, *rel_paths, content="const a = 1;\n"):
    for rel in rel_paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


# --- constants ---------------------------------------------------------------------


def test_default_excludes_are_the_19_names_in_order():
    assert Constants.DEFAULT_EXCLUDES == [
        "node_modules", "dist", "build", ".git", "vendor", "third_party", ".next",
        "__pycache__", ".cache", "coverage", ".nuxt", "out", "target", ".turbo",
        ".svelte-kit", ".output", ".vercel", ".parcel-cache", "storybook-static",
    ]


def test_extensions():
    assert Constants.EXTENSIONS == [".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"]


# --- extensions --------------------------------------------------------------------


@pytest.mark.parametrize("ext", Constants.EXTENSIONS)
@pytest.mark.parametrize("case", [str.lower, str.upper])
def test_each_extension_in_any_case_is_selected(tmp_path, ext, case):
    name = f"file{case(ext)}"
    _touch(tmp_path, name, "README.md", "style.css", "a.vue")

    assert select_files(tmp_path, tmp_path).lines == [name]


def test_directory_lines_are_sorted_posix_and_relative(tmp_path):
    _touch(tmp_path, "z.js", "src/b.ts", "src/a.tsx", "ext/UPPER.JS", "notes.txt")

    selection = select_files(tmp_path, tmp_path)

    assert selection == Selection(
        tmp_path, ["ext/UPPER.JS", "src/a.tsx", "src/b.ts", "z.js"], []
    )


# --- declaration files -------------------------------------------------------------


@pytest.mark.parametrize("name", ["types.d.ts", "a.d.mts", "b.d.cts", "C.D.TS", "x.D.Mts"])
def test_declaration_files_are_skipped_in_a_directory(tmp_path, name):
    _touch(tmp_path, f"ext/{name}", "keep.ts")

    assert select_files(tmp_path, tmp_path) == Selection(tmp_path, ["keep.ts"], [])


@pytest.mark.parametrize("name", ["types.d.ts", "a.d.mts", "b.d.cts"])
def test_declaration_single_file_selects_nothing(tmp_path, name):
    _touch(tmp_path, name)

    assert select_files(tmp_path / name, tmp_path).lines == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [("a.d.ts", True), ("A.D.CTS", True), ("a.ts", False), ("d.ts", False), ("a.d.tsx", False)],
)
def test_is_declaration(name, expected):
    assert is_declaration(Path("dir") / name) is expected


# --- default excludes --------------------------------------------------------------


@pytest.mark.parametrize("excluded", Constants.DEFAULT_EXCLUDES + ["Node_Modules", "BUILD"])
def test_directory_default_excludes(tmp_path, excluded):
    _touch(tmp_path, f"{excluded}/skip.js", "keep.js")

    assert select_files(tmp_path, tmp_path).lines == ["keep.js"]


def test_extra_excludes_replace_the_defaults_when_given(tmp_path):
    _touch(tmp_path, "dist/a.js", "spec/b.js")

    assert select_files(tmp_path, tmp_path, excludes=["spec"]).lines == ["dist/a.js"]


def test_single_file_inside_excluded_dir_is_kept(tmp_path):
    _touch(tmp_path, "dist/a.js")

    assert select_files(tmp_path / "dist" / "a.js", tmp_path / "dist").lines == ["a.js"]


# --- gitignore ---------------------------------------------------------------------


def test_gitignore_is_off_by_default(tmp_path, fake_git):
    _touch(tmp_path, "a.js", "ignored.js")
    fake_git["result"] = GitIgnored({tmp_path.resolve() / "ignored.js"}, [])

    assert select_files(tmp_path, tmp_path).lines == ["a.js", "ignored.js"]
    assert fake_git["calls"] == []


# --- symlinks ----------------------------------------------------------------------


def test_symlink_inside_is_reported_as_target_once(tmp_path):
    _touch(tmp_path, "lib/real.js")
    (tmp_path / "link.js").symlink_to("lib/real.js")

    assert select_files(tmp_path, tmp_path).lines == ["lib/real.js"]


def test_symlink_outside_is_skipped(tmp_path):
    project = tmp_path / "project"
    _touch(tmp_path, "outside.js", "project/a.js")
    (project / "out.js").symlink_to(tmp_path / "outside.js")

    assert select_files(project, project).lines == ["a.js"]


def test_dangling_symlink_is_skipped(tmp_path):
    _touch(tmp_path, "a.js")
    (tmp_path / "dangling.js").symlink_to(tmp_path / "missing.js")

    assert select_files(tmp_path, tmp_path).lines == ["a.js"]


def test_symlink_named_as_declaration_is_skipped(tmp_path):
    _touch(tmp_path, "real.ts")
    (tmp_path / "link.d.ts").symlink_to("real.ts")

    assert select_files(tmp_path, tmp_path).lines == ["real.ts"]


# --- contents and names ------------------------------------------------------------


def test_non_utf8_content_is_still_selected(tmp_path):
    (tmp_path / "latin1.js").write_bytes(b"var s = '\xe9';\n")

    assert select_files(tmp_path, tmp_path).lines == ["latin1.js"]


def test_unsendable_names_are_warned():
    root = Path("/project")
    files = [root / "b.js", root / "a\nb.js", root / "lib" / NON_UTF8, root / "a.ts"]

    selection = build_selection(root, files)

    assert selection.lines == ["a.ts", "b.js"]
    assert selection.skipped == [
        "skipping file with a newline in its name: 'a\\nb.js'",
        f"skipping file whose name is not valid UTF-8: {'lib/' + NON_UTF8!r}",
    ]


def test_newline_name_on_disk_is_warned(tmp_path):
    _touch(tmp_path, "ok.js", "a\nb.js")

    selection = select_files(tmp_path, tmp_path)

    assert selection.lines == ["ok.js"]
    assert selection.skipped == ["skipping file with a newline in its name: 'a\\nb.js'"]


def test_unsendable_reason_plain_names_are_fine():
    assert unsendable_reason("dir with space/tab\tname é.ts") is None


# --- single file -------------------------------------------------------------------


def test_single_file_sends_only_its_name(tmp_path):
    _touch(tmp_path, "a.ts", "b.ts")

    selection = select_files(tmp_path / "a.ts", tmp_path)

    assert selection.root == tmp_path
    assert selection.lines == ["a.ts"]


@pytest.mark.parametrize("name", ["a.py", "a.vue", "a.json", "README"])
def test_single_file_with_unsupported_extension_selects_nothing(tmp_path, name):
    _touch(tmp_path, name)

    assert select_files(tmp_path / name, tmp_path).lines == []


def test_empty_directory_selects_nothing(tmp_path):
    assert select_files(tmp_path, tmp_path) == Selection(tmp_path, [], [])
