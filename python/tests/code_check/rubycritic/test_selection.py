"""Unit tests for code_check.rubycritic.selection."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.selection import (
    Selection,
    build_selection,
    select_files,
    unsendable_reason,
)

NON_UTF8 = b"bad\xff.rb".decode("utf-8", "surrogateescape")


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths (no real git); returns the roots it was called with."""
    state = {"calls": [], "result": None}

    def ignored_paths(root):
        state["calls"].append(root)
        return state["result"]

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(ignored_paths))
    return state


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


def test_directory_gitignore_applied_by_default(tmp_path, fake_git):
    _touch(tmp_path, "a.rb", "ignored.rb", "gen/b.rb")
    root = tmp_path.resolve()
    fake_git["result"] = GitIgnored({root / "ignored.rb"}, [root / "gen"])

    assert select_files(tmp_path, tmp_path).lines == ["a.rb"]
    assert fake_git["calls"] == [root]


def test_directory_gitignore_off_skips_git(tmp_path, fake_git):
    _touch(tmp_path, "a.rb", "ignored.rb")
    fake_git["result"] = GitIgnored({tmp_path.resolve() / "ignored.rb"}, [])

    assert select_files(tmp_path, tmp_path, gitignore=False).lines == ["a.rb", "ignored.rb"]
    assert fake_git["calls"] == []


def test_directory_gitignore_unknown_drops_nothing(tmp_path, fake_git):
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


def test_build_selection_dedups_by_resolved_path(tmp_path):
    _touch(tmp_path, "a.rb")
    (tmp_path / "link.rb").symlink_to(tmp_path / "a.rb")

    selection = build_selection(tmp_path, [tmp_path / "link.rb", tmp_path / "a.rb"])

    assert selection.lines == ["a.rb"]


# --- flags -------------------------------------------------------------------------


def test_extra_excludes(tmp_path):
    _touch(tmp_path, "spec/a_spec.rb", "db/schema.rb", "app/a.rb")
    excludes = [*Constants.DEFAULT_EXCLUDES, "spec", "DB"]

    assert select_files(tmp_path, tmp_path, excludes=excludes).lines == ["app/a.rb"]


def test_excludes_match_file_name_component(tmp_path):
    _touch(tmp_path, "app/skip.rb", "app/keep.rb")

    assert select_files(tmp_path, tmp_path, excludes=["skip.rb"]).lines == ["app/keep.rb"]


def test_no_default_excludes(tmp_path):
    _touch(tmp_path, "tmp/a.rb", "vendor/b.rb", "spec/c.rb")

    assert select_files(tmp_path, tmp_path, excludes=["spec"]).lines == ["tmp/a.rb", "vendor/b.rb"]


def test_ignore_globs(tmp_path):
    _touch(tmp_path, "app/a.rb", "app/a_spec.rb", "db/migrate/1.rb", "db/seeds.rb")

    selection = select_files(tmp_path, tmp_path, ignore=["*_spec.rb", "db/migrate/**", ""])

    assert selection.lines == ["app/a.rb", "db/seeds.rb"]


def test_ignore_anchored_glob(tmp_path):
    _touch(tmp_path, "a.rb", "lib/a.rb")

    assert select_files(tmp_path, tmp_path, ignore=["/a.rb"]).lines == ["lib/a.rb"]


def test_include_globs_combine_with_rb(tmp_path):
    _touch(tmp_path, "app/a.rb", "app/b.erb", "app/c.txt", "lib/d.rb", "z.rb")

    selection = select_files(tmp_path, tmp_path, include=["app/**", "lib/**"])

    assert selection.lines == ["app/a.rb", "lib/d.rb"]


def test_include_is_case_insensitive(tmp_path):
    _touch(tmp_path, "App/a.rb", "lib/b.rb")

    assert select_files(tmp_path, tmp_path, include=["app/**"]).lines == ["App/a.rb"]


# --- filter order ------------------------------------------------------------------


def test_filter_order_first_rejecting_step_wins(tmp_path, fake_git):
    _touch(tmp_path, "tmp/a.rb", "spec/b.rb", "gen/c.rb", "lib/d.rb", "lib/e.rb")
    root = tmp_path.resolve()
    # tmp/a.rb matches every step; only the default excludes should drop it.
    fake_git["result"] = GitIgnored({root / "lib" / "d.rb"}, [root / "tmp", root / "gen"])

    selection = select_files(
        tmp_path,
        tmp_path,
        excludes=[*Constants.DEFAULT_EXCLUDES, "spec"],
        ignore=["tmp/**", "spec/**", "gen/**", "lib/d.rb"],
        include=["lib/**"],
    )

    assert selection.lines == ["lib/e.rb"]


def test_filter_order_include_does_not_rescue_excluded(tmp_path):
    _touch(tmp_path, "vendor/a.rb", "lib/b.rb")

    assert select_files(tmp_path, tmp_path, include=["vendor/**", "lib/**"]).lines == ["lib/b.rb"]


# --- single file with flags --------------------------------------------------------


def test_single_file_extra_excludes_do_not_apply(tmp_path):
    _touch(tmp_path, "spec/a.rb")
    target = tmp_path / "spec" / "a.rb"

    selection = select_files(target, target.parent, excludes=["spec", "a.rb"])

    assert selection.lines == ["a.rb"]


def test_single_file_globs_match_the_file_name(tmp_path):
    _touch(tmp_path, "lib/a_spec.rb")
    target = tmp_path / "lib" / "a_spec.rb"

    assert select_files(target, target.parent, ignore=["*_spec.rb"]).lines == []
    assert select_files(target, target.parent, ignore=["lib/*_spec.rb"]).lines == ["a_spec.rb"]
    assert select_files(target, target.parent, include=["a_*"]).lines == ["a_spec.rb"]
    assert select_files(target, target.parent, include=["lib/**"]).lines == []


def test_single_file_gitignore_uses_parent(tmp_path, fake_git):
    _touch(tmp_path, "ignored.rb", "kept.rb")
    root = tmp_path.resolve()
    fake_git["result"] = GitIgnored({root / "ignored.rb"}, [])

    assert select_files(tmp_path / "ignored.rb", tmp_path).lines == []
    assert select_files(tmp_path / "kept.rb", tmp_path).lines == ["kept.rb"]
    assert fake_git["calls"] == [root, root]


# --- symlinks ----------------------------------------------------------------------


def test_relative_symlink_inside_is_reported_as_target_once(tmp_path):
    _touch(tmp_path, "lib/real.rb")
    (tmp_path / "link.rb").symlink_to("lib/real.rb")

    assert select_files(tmp_path, tmp_path).lines == ["lib/real.rb"]


def test_symlink_inside_kept_when_target_filtered_out(tmp_path):
    _touch(tmp_path, "tmp/real.rb")
    (tmp_path / "link.rb").symlink_to("tmp/real.rb")

    assert select_files(tmp_path, tmp_path).lines == ["tmp/real.rb"]


def test_absolute_symlink_inside_is_kept_as_target(tmp_path):
    _touch(tmp_path, "lib/real.rb")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "link.rb").symlink_to((tmp_path / "lib" / "real.rb").resolve())

    assert select_files(tmp_path, tmp_path, ignore=["lib/**"]).lines == ["lib/real.rb"]


def test_symlink_outside_is_skipped(tmp_path):
    project = tmp_path / "project"
    _touch(tmp_path, "outside.rb", "project/a.rb")
    (project / "out.rb").symlink_to(tmp_path / "outside.rb")

    assert select_files(project, project).lines == ["a.rb"]


def test_dangling_symlink_is_skipped(tmp_path):
    _touch(tmp_path, "a.rb")
    (tmp_path / "dangling.rb").symlink_to(tmp_path / "missing.rb")

    assert select_files(tmp_path, tmp_path).lines == ["a.rb"]


def test_directory_symlink_is_not_walked(tmp_path):
    _touch(tmp_path, "lib/a.rb")
    (tmp_path / "linked").symlink_to(tmp_path / "lib", target_is_directory=True)

    assert select_files(tmp_path, tmp_path).lines == ["lib/a.rb"]


def test_single_file_symlink_outside_root_is_skipped(tmp_path):
    _touch(tmp_path, "outside.rb")
    (tmp_path / "project").mkdir()
    link = tmp_path / "project" / "link.rb"
    link.symlink_to(tmp_path / "outside.rb")

    assert select_files(link, link.parent).lines == []


def test_non_utf8_ruby_file_is_kept_with_flags(tmp_path):
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "bad.rb").write_bytes(b"\xff\xfe" + "é".encode() * 600)

    assert select_files(tmp_path, tmp_path, include=["lib/**"]).lines == ["lib/bad.rb"]
