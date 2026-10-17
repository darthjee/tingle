"""Unit tests for code_check.php_complexity.selection."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.php_complexity.constants import Constants
from code_check.php_complexity.selection import (
    Selection,
    build_selection,
    in_bootstrap_cache,
    is_blade,
    select_files,
    unsendable_reason,
)

NON_UTF8 = b"bad\xff.php".decode("utf-8", "surrogateescape")


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths (no real git); returns the roots it was called with."""
    state = {"calls": [], "result": None}

    def ignored_paths(root):
        state["calls"].append(root)
        return state["result"]

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(ignored_paths))
    return state


def _touch(root, *rel_paths, content="<?php\n$a = 1;\n"):
    for rel in rel_paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


# --- constants ---------------------------------------------------------------------


def test_default_excludes_are_the_16_names_in_order():
    assert Constants.DEFAULT_EXCLUDES == [
        "node_modules", "dist", "build", ".git", "vendor", "third_party", ".next",
        "__pycache__", ".cache", "coverage", ".nuxt", "out", "target",
        "var", "storage", ".phpunit.cache",
    ]


def test_extensions_and_skip_constants():
    assert Constants.EXTENSIONS == [".php"]
    assert Constants.BLADE_SUFFIX == ".blade.php"
    assert Constants.BOOTSTRAP_CACHE == ("bootstrap", "cache")
    assert Constants.IMAGE_REPO == "darthjee/tingle_php_complexity"


def test_thresholds():
    assert (Constants.DEFAULT_WARN, Constants.DEFAULT_ERROR, Constants.DEFAULT_CRITICAL) == (
        20, 40, 60,
    )


# --- extensions --------------------------------------------------------------------


@pytest.mark.parametrize("name", ["file.php", "FILE.PHP", "Mixed.Php"])
def test_php_in_any_case_is_selected(tmp_path, name):
    _touch(tmp_path, name, "README.md", "notes.txt", "a.js", "a.phtml", "a.inc")

    assert select_files(tmp_path, tmp_path).lines == [name]


def test_directory_lines_are_sorted_posix_and_relative(tmp_path):
    _touch(tmp_path, "z.php", "src/b.php", "src/a.php", "ext/UPPER.PHP", "notes.txt")

    selection = select_files(tmp_path, tmp_path)

    assert selection == Selection(
        tmp_path, ["ext/UPPER.PHP", "src/a.php", "src/b.php", "z.php"], []
    )


# --- Blade templates ---------------------------------------------------------------


@pytest.mark.parametrize("name", ["welcome.blade.php", "A.BLADE.PHP", "x.Blade.Php"])
def test_blade_templates_are_skipped_in_a_directory(tmp_path, name):
    _touch(tmp_path, f"views/{name}", "keep.php")

    assert select_files(tmp_path, tmp_path) == Selection(tmp_path, ["keep.php"], [])


@pytest.mark.parametrize("name", ["welcome.blade.php", "W.BLADE.PHP"])
def test_blade_single_file_selects_nothing(tmp_path, name):
    _touch(tmp_path, name)

    assert select_files(tmp_path / name, tmp_path).lines == []


def test_blade_is_skipped_even_when_included(tmp_path):
    _touch(tmp_path, "a.blade.php", "b.php")

    assert select_files(tmp_path, tmp_path, include=["*.blade.php"]).lines == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("a.blade.php", True),
        ("A.BLADE.PHP", True),
        ("blade.php", False),
        ("a.php", False),
        ("a.blade.phtml", False),
    ],
)
def test_is_blade(name, expected):
    assert is_blade(Path("dir") / name) is expected


# --- bootstrap/cache ---------------------------------------------------------------


@pytest.mark.parametrize(
    "rel", ["bootstrap/cache/services.php", "app/Bootstrap/Cache/x.php", "a/bootstrap/cache/b/c.php"]
)
def test_bootstrap_cache_is_skipped(tmp_path, rel):
    _touch(tmp_path, rel, "keep.php")

    assert select_files(tmp_path, tmp_path).lines == ["keep.php"]


@pytest.mark.parametrize(
    "rel",
    ["bootstrap/app.php", "cache/bootstrap/x.php", "bootstrap/other/cache/x.php", "bootstrap/cache.php"],
)
def test_bootstrap_cache_rule_needs_adjacent_directories(tmp_path, rel):
    _touch(tmp_path, rel)

    assert select_files(tmp_path, tmp_path).lines == [rel]


def test_bootstrap_cache_can_be_turned_off(tmp_path):
    _touch(tmp_path, "bootstrap/cache/services.php")

    selection = select_files(tmp_path, tmp_path, skip_bootstrap_cache=False)

    assert selection.lines == ["bootstrap/cache/services.php"]


def test_target_inside_cache_directory_keeps_its_files(tmp_path):
    _touch(tmp_path, "bootstrap/cache/services.php")
    target = tmp_path / "bootstrap" / "cache"

    assert select_files(target, target).lines == ["services.php"]


def test_bootstrap_cache_rule_does_not_apply_to_a_single_file(tmp_path):
    _touch(tmp_path, "bootstrap/cache/services.php")
    target = tmp_path / "bootstrap" / "cache" / "services.php"

    assert select_files(target, target.parent).lines == ["services.php"]


def test_in_bootstrap_cache_outside_target_is_false():
    assert in_bootstrap_cache(Path("/other/bootstrap/cache/a.php"), Path("/project")) is False


# --- default excludes --------------------------------------------------------------


@pytest.mark.parametrize("excluded", Constants.DEFAULT_EXCLUDES + ["Vendor", "STORAGE"])
def test_directory_default_excludes(tmp_path, excluded):
    _touch(tmp_path, f"{excluded}/skip.php", "keep.php")

    assert select_files(tmp_path, tmp_path).lines == ["keep.php"]


def test_extra_excludes_replace_the_defaults_when_given(tmp_path):
    _touch(tmp_path, "vendor/a.php", "spec/b.php")

    assert select_files(tmp_path, tmp_path, excludes=["spec"]).lines == ["vendor/a.php"]


def test_single_file_inside_excluded_dir_is_kept(tmp_path):
    _touch(tmp_path, "vendor/a.php")

    assert select_files(tmp_path / "vendor" / "a.php", tmp_path / "vendor").lines == ["a.php"]


# --- gitignore ---------------------------------------------------------------------


def test_gitignore_is_off_by_default(tmp_path, fake_git):
    _touch(tmp_path, "a.php", "ignored.php")
    fake_git["result"] = GitIgnored({tmp_path.resolve() / "ignored.php"}, [])

    assert select_files(tmp_path, tmp_path).lines == ["a.php", "ignored.php"]
    assert fake_git["calls"] == []


# --- symlinks ----------------------------------------------------------------------


def test_symlink_inside_is_reported_as_target_once(tmp_path):
    _touch(tmp_path, "lib/real.php")
    (tmp_path / "link.php").symlink_to("lib/real.php")

    assert select_files(tmp_path, tmp_path).lines == ["lib/real.php"]


def test_symlink_outside_is_skipped(tmp_path):
    project = tmp_path / "project"
    _touch(tmp_path, "outside.php", "project/a.php")
    (project / "out.php").symlink_to(tmp_path / "outside.php")

    assert select_files(project, project).lines == ["a.php"]


def test_dangling_symlink_is_skipped(tmp_path):
    _touch(tmp_path, "a.php")
    (tmp_path / "dangling.php").symlink_to(tmp_path / "missing.php")

    assert select_files(tmp_path, tmp_path).lines == ["a.php"]


def test_symlink_named_as_blade_is_skipped(tmp_path):
    _touch(tmp_path, "real.php")
    (tmp_path / "link.blade.php").symlink_to("real.php")

    assert select_files(tmp_path, tmp_path).lines == ["real.php"]


# --- contents and names ------------------------------------------------------------


def test_non_utf8_content_is_still_selected(tmp_path):
    (tmp_path / "latin1.php").write_bytes(b"<?php\n$s = '\xe9';\n")

    assert select_files(tmp_path, tmp_path).lines == ["latin1.php"]


def test_unsendable_names_are_warned():
    root = Path("/project")
    files = [root / "b.php", root / "a\nb.php", root / "lib" / NON_UTF8, root / "a.php"]

    selection = build_selection(root, files)

    assert selection.lines == ["a.php", "b.php"]
    assert selection.skipped == [
        "skipping file with a newline in its name: 'a\\nb.php'",
        f"skipping file whose name is not valid UTF-8: {'lib/' + NON_UTF8!r}",
    ]


def test_newline_name_on_disk_is_warned(tmp_path):
    _touch(tmp_path, "ok.php", "a\nb.php")

    selection = select_files(tmp_path, tmp_path)

    assert selection.lines == ["ok.php"]
    assert selection.skipped == ["skipping file with a newline in its name: 'a\\nb.php'"]


def test_unsendable_reason_plain_names_are_fine():
    assert unsendable_reason("dir with space/tab\tname é.php") is None


# --- single file -------------------------------------------------------------------


def test_single_file_sends_only_its_name(tmp_path):
    _touch(tmp_path, "a.php", "b.php")

    selection = select_files(tmp_path / "a.php", tmp_path)

    assert selection.root == tmp_path
    assert selection.lines == ["a.php"]


@pytest.mark.parametrize("name", ["a.py", "a.js", "a.phtml", "README"])
def test_single_file_with_unsupported_extension_selects_nothing(tmp_path, name):
    _touch(tmp_path, name)

    assert select_files(tmp_path / name, tmp_path).lines == []


def test_empty_directory_selects_nothing(tmp_path):
    assert select_files(tmp_path, tmp_path) == Selection(tmp_path, [], [])
