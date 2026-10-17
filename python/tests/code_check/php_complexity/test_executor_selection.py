"""File-selection tests for code_check.php_complexity.executor.CheckPhpComplexity.

Docker is mocked: the fake container echoes back one entry per line it reads
on stdin, so each test asserts on the file list the executor sent. git is real
(no `GitIgnore` stub here); the git-dependent tests are skipped without git.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from code_check.php_complexity import docker_runner
from code_check.php_complexity.constants import Constants
from code_check.php_complexity.executor import CheckPhpComplexity
from tests.code_check.php_complexity.sample_output import entry, output

REAL_RUN = subprocess.run

NO_FILES = CheckPhpComplexity.NO_FILES_MESSAGE

needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")


class EchoDocker:
    """Scripted `docker`: every sub-command succeeds and `run` echoes stdin as results."""

    def __init__(self):
        self.calls = []

    def __call__(self, args, **kwargs):
        if args[0] != "docker":  # `subprocess` is shared: let the git calls through
            return REAL_RUN(args, **kwargs)
        self.calls.append((args, kwargs))
        if args[1] != "run":
            return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")
        lines = kwargs["input"].decode().splitlines()
        stdout = json.dumps(output([entry(line, 1) for line in lines])).encode()
        return SimpleNamespace(returncode=0, stdout=stdout, stderr=b"")

    def stdin(self):
        """Return the lines sent to the container, or None when it never ran."""
        runs = [k for a, k in self.calls if a[1] == "run"]
        if not runs:
            return None
        return runs[0]["input"].decode().splitlines()


@pytest.fixture(autouse=True)
def no_git_env(monkeypatch, tmp_path):
    """Keep git hermetic: no global/system config, never look above tmp_path."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.resolve().parent))


@pytest.fixture
def docker(monkeypatch):
    fake = EchoDocker()
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr(docker_runner.subprocess, "run", fake)
    return fake


def _touch(root, *rel_paths):
    for rel in rel_paths:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<?php\n")


def _run(*args):
    try:
        CheckPhpComplexity().run([*args, "--image", "img"])
    except SystemExit as exc:
        return exc.code
    return 0


def _git(repo, *args):
    REAL_RUN(["git", "-C", str(repo), *args], check=True, capture_output=True)


# --- --exclude ---------------------------------------------------------------------


def test_exclude_adds_to_the_defaults(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "tests/a.php", "fixtures/b.php", "vendor/c.php")

    assert _run(str(tmp_path), "--exclude", "tests,fixtures") == 0

    assert docker.stdin() == ["keep.php"]


def test_second_exclude_replaces_the_first(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "tests/a.php", "fixtures/b.php")

    _run(str(tmp_path), "--exclude", "tests", "--exclude", "fixtures")

    assert docker.stdin() == ["keep.php", "tests/a.php"]


def test_blank_exclude_entries_are_dropped(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "tests/a.php")

    assert _run(str(tmp_path), "--exclude", " , tests ,,") == 0

    assert docker.stdin() == ["keep.php"]


def test_exclude_is_case_insensitive(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "Tests/a.php")

    _run(str(tmp_path), "--exclude", "tests")

    assert docker.stdin() == ["keep.php"]


def test_exclude_bootstrap_cache_matches_nothing(tmp_path, capsys, docker):
    _touch(tmp_path, "bootstrap/cache/services.php", "keep.php")

    _run(str(tmp_path), "--no-default-excludes", "--exclude", "bootstrap/cache")

    assert docker.stdin() == ["bootstrap/cache/services.php", "keep.php"]


def test_default_excludes_constant_is_used(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", *(f"{name}/x.php" for name in Constants.DEFAULT_EXCLUDES))

    _run(str(tmp_path), "--exclude", "extra")

    assert docker.stdin() == ["keep.php"]


# --- --no-default-excludes ---------------------------------------------------------

DEFAULT_SKIPPED = ("vendor/a.php", "storage/b.php", "bootstrap/cache/services.php")


def test_default_run_skips_vendor_storage_and_bootstrap_cache(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", *DEFAULT_SKIPPED)

    _run(str(tmp_path))

    assert docker.stdin() == ["keep.php"]


def test_no_default_excludes_alone(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "welcome.blade.php", "views/V.BLADE.PHP", *DEFAULT_SKIPPED)

    _run(str(tmp_path), "--no-default-excludes")

    assert docker.stdin() == [
        "bootstrap/cache/services.php", "keep.php", "storage/b.php", "vendor/a.php",
    ]


def test_no_default_excludes_with_exclude(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "welcome.blade.php", *DEFAULT_SKIPPED)

    _run(str(tmp_path), "--no-default-excludes", "--exclude", "vendor")

    assert docker.stdin() == ["bootstrap/cache/services.php", "keep.php", "storage/b.php"]


# --- Blade templates ---------------------------------------------------------------


@pytest.mark.parametrize("name", ["welcome.blade.php", "View.BLADE.PHP", "x.Blade.Php"])
def test_blade_templates_are_skipped_in_any_case(tmp_path, capsys, docker, name):
    _touch(tmp_path, "keep.php", f"views/{name}")

    _run(str(tmp_path))

    assert docker.stdin() == ["keep.php"]


def test_include_does_not_rescue_blade_templates(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.php", "views/welcome.blade.php", "View.BLADE.PHP")

    assert _run(str(tmp_path), "--include", "**/*.blade.php") == 0

    assert docker.stdin() is None
    assert NO_FILES in capsys.readouterr().out


@pytest.mark.parametrize("extra", [[], ["--no-default-excludes"]])
def test_blade_single_file_is_skipped(tmp_path, capsys, docker, extra):
    _touch(tmp_path, "welcome.blade.php")

    assert _run(str(tmp_path / "welcome.blade.php"), *extra) == 0

    assert docker.calls == []
    assert NO_FILES in capsys.readouterr().out


# --- bootstrap/cache ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("rel", "selected"),
    [
        ("bootstrap/cache/services.php", False),
        ("app/Bootstrap/Cache/x.php", False),
        ("bootstrap/cache/deep/x.php", False),
        ("bootstrap/app.php", True),
        ("cache/bootstrap/x.php", True),
        ("bootstrap/other/cache/x.php", True),
        ("bootstrap/cache.php", True),
    ],
)
def test_bootstrap_cache_rule(tmp_path, capsys, docker, rel, selected):
    _touch(tmp_path, "keep.php", rel)

    _run(str(tmp_path))

    assert docker.stdin() == sorted(["keep.php", *([rel] if selected else [])])


def test_path_inside_a_cache_directory_keeps_its_files(tmp_path, capsys, docker):
    _touch(tmp_path, "app/bootstrap/cache/services.php", "app/bootstrap/cache/packages.php")

    _run(str(tmp_path / "app" / "bootstrap" / "cache"))

    assert docker.stdin() == ["packages.php", "services.php"]


def test_single_file_under_bootstrap_cache_is_analysed(tmp_path, capsys, docker):
    _touch(tmp_path, "bootstrap/cache/services.php")

    assert _run(str(tmp_path / "bootstrap" / "cache" / "services.php")) == 0

    assert docker.stdin() == ["services.php"]


# --- --ignore and --include --------------------------------------------------------


def test_ignore_is_repeatable(tmp_path, capsys, docker):
    _touch(tmp_path, "src/a.php", "src/aTest.php", "tests/b.php")

    _run(str(tmp_path), "--ignore", "**/*Test.php", "--ignore", "tests/**")

    assert docker.stdin() == ["src/a.php"]


def test_include_is_repeatable(tmp_path, capsys, docker):
    _touch(tmp_path, "src/a.php", "lib/b.php", "scripts/c.php")

    _run(str(tmp_path), "--include", "src/**", "--include", "lib/**")

    assert docker.stdin() == ["lib/b.php", "src/a.php"]


def test_globs_are_case_insensitive(tmp_path, capsys, docker):
    _touch(tmp_path, "Src/A.php", "lib/b.php")

    _run(str(tmp_path), "--include", "src/**")

    assert docker.stdin() == ["Src/A.php"]


def test_include_and_extension_must_both_match(tmp_path, capsys, docker):
    _touch(tmp_path, "a.php", "data.json", "page.phtml", "lib.inc")

    assert _run(str(tmp_path), "--include", "**/*.json", "--include", "*.phtml",
                "--include", "*.inc") == 0

    assert docker.stdin() is None
    assert NO_FILES in capsys.readouterr().out


def test_ignore_wins_over_include(tmp_path, capsys, docker):
    _touch(tmp_path, "src/a.php", "src/b.php")

    _run(str(tmp_path), "--include", "src/**", "--ignore", "src/b.php")

    assert docker.stdin() == ["src/a.php"]


def test_include_does_not_rescue_excluded_directories(tmp_path, capsys, docker):
    _touch(tmp_path, "vendor/a.php", "lib/b.php")

    _run(str(tmp_path), "--include", "vendor/**", "--include", "lib/**")

    assert docker.stdin() == ["lib/b.php"]


def test_include_does_not_rescue_bootstrap_cache(tmp_path, capsys, docker):
    _touch(tmp_path, "bootstrap/cache/services.php", "bootstrap/app.php")

    _run(str(tmp_path), "--include", "bootstrap/**")

    assert docker.stdin() == ["bootstrap/app.php"]


# --- extensions --------------------------------------------------------------------


def test_upper_case_extension_is_selected(tmp_path, capsys, docker):
    _touch(tmp_path, "UPPER.PHP", "Mixed.Php", "a.php3", "b.php8", "c.phtml", "d.inc")

    _run(str(tmp_path))

    assert docker.stdin() == ["Mixed.Php", "UPPER.PHP"]


# --- .gitignore --------------------------------------------------------------------


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / ".gitignore").write_text("*.gen.php\ngenerated/\n")
    _touch(repo, "main.php", "skip.gen.php", "kept.gen.php", "generated/x.php")
    _git(repo, "add", "-f", "kept.gen.php")
    return repo


@needs_git
def test_gitignore_is_on_by_default(repo, capsys, docker):
    assert _run(str(repo)) == 0

    assert docker.stdin() == ["kept.gen.php", "main.php"]
    assert capsys.readouterr().err == ""


@needs_git
def test_no_gitignore_keeps_ignored_files(repo, capsys, docker):
    _run(str(repo), "--no-gitignore")

    assert docker.stdin() == ["generated/x.php", "kept.gen.php", "main.php", "skip.gen.php"]


@needs_git
def test_gitignore_applies_to_a_single_file(repo, capsys, docker):
    assert _run(str(repo / "skip.gen.php")) == 0

    assert docker.stdin() is None
    assert NO_FILES in capsys.readouterr().out


@needs_git
def test_no_gitignore_keeps_an_ignored_single_file(repo, capsys, docker):
    assert _run(str(repo / "skip.gen.php"), "--no-gitignore") == 0

    assert docker.stdin() == ["skip.gen.php"]


def test_outside_a_work_tree_nothing_is_skipped_or_printed(tmp_path, capsys, docker):
    (tmp_path / ".gitignore").write_text("*.php\n")
    _touch(tmp_path, "a.php")

    assert _run(str(tmp_path)) == 0

    assert docker.stdin() == ["a.php"]
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "git" not in captured.out.lower()


def test_missing_git_prints_nothing(tmp_path, capsys, docker, monkeypatch):
    _touch(tmp_path, "a.php")
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))

    assert _run(str(tmp_path)) == 0

    assert docker.stdin() == ["a.php"]
    assert capsys.readouterr().err == ""


# --- filter order ------------------------------------------------------------------


@needs_git
def test_filter_order_first_rejecting_step_wins(repo, capsys, docker):
    # Every candidate except lib/d.php matches several steps; all are dropped.
    _touch(
        repo, "vendor/a.php", "tests/b.php", "lib/c.php", "lib/d.php",
        "lib/e.blade.php", "lib/bootstrap/cache/f.php",
    )

    _run(
        str(repo), "--exclude", "tests",
        "--ignore", "vendor/**", "--ignore", "tests/**", "--ignore", "lib/c.php",
        "--include", "lib/**", "--include", "generated/**", "--include", "vendor/**",
    )

    assert docker.stdin() == ["lib/d.php"]


# --- single-file <path> ------------------------------------------------------------


def test_single_file_directory_excludes_do_not_apply(tmp_path, capsys, docker):
    _touch(tmp_path, "vendor/tests/a.php")

    _run(str(tmp_path / "vendor" / "tests" / "a.php"), "--exclude", "tests,a.php")

    assert docker.stdin() == ["a.php"]


@pytest.mark.parametrize(
    ("flag", "glob", "selected"),
    [
        ("--ignore", "a.php", False),
        ("--ignore", "*.inc", True),
        ("--include", "a.*", True),
        ("--include", "tests/**", False),
    ],
)
def test_single_file_globs_match_the_file_name(tmp_path, capsys, docker, flag, glob, selected):
    _touch(tmp_path, "tests/a.php")

    assert _run(str(tmp_path / "tests" / "a.php"), flag, glob) == 0

    assert docker.stdin() == (["a.php"] if selected else None)


# --- symlinks ----------------------------------------------------------------------


def test_symlinks_inside_outside_absolute_and_dangling(tmp_path, capsys, docker):
    project = tmp_path / "project"
    _touch(tmp_path, "outside.php", "project/lib/real.php", "project/lib/abs.php")
    (project / "rel.php").symlink_to("lib/real.php")
    (project / "abs_inside.php").symlink_to(project / "lib" / "abs.php")
    (project / "out.php").symlink_to(tmp_path / "outside.php")
    (project / "dangling.php").symlink_to(project / "missing.php")

    _run(str(project))

    assert docker.stdin() == ["lib/abs.php", "lib/real.php"]


def test_symlinked_single_file_is_resolved(tmp_path, capsys, docker):
    _touch(tmp_path, "real/target.php")
    (tmp_path / "link.php").symlink_to(tmp_path / "real" / "target.php")

    _run(str(tmp_path / "link.php"))

    assert docker.stdin() == ["target.php"]
