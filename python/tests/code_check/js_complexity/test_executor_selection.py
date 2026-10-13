"""File-selection tests for code_check.js_complexity.executor.CheckJsComplexity.

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

from code_check.js_complexity import docker_runner
from code_check.js_complexity.constants import Constants
from code_check.js_complexity.executor import CheckJsComplexity
from tests.code_check.js_complexity.sample_output import entry, output

REAL_RUN = subprocess.run

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
        stdout = json.dumps(output([entry(line, 1.0) for line in lines])).encode()
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
        path.write_text("const a = 1;\n")


def _run(*args):
    try:
        CheckJsComplexity().run([*args, "--image", "img"])
    except SystemExit as exc:
        return exc.code
    return 0


def _git(repo, *args):
    REAL_RUN(["git", "-C", str(repo), *args], check=True, capture_output=True)


# --- --exclude ---------------------------------------------------------------------


def test_exclude_adds_to_the_defaults(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.js", "test/a.js", "fixtures/b.js", "dist/c.js")

    assert _run(str(tmp_path), "--exclude", "test,fixtures") == 0

    assert docker.stdin() == ["keep.js"]


def test_second_exclude_replaces_the_first(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.js", "test/a.js", "fixtures/b.js")

    _run(str(tmp_path), "--exclude", "test", "--exclude", "fixtures")

    assert docker.stdin() == ["keep.js", "test/a.js"]


def test_blank_exclude_entries_are_dropped(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.js", "test/a.js")

    assert _run(str(tmp_path), "--exclude", " , test ,,") == 0

    assert docker.stdin() == ["keep.js"]


# --- --no-default-excludes ---------------------------------------------------------


def test_no_default_excludes_alone(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.js", "dist/a.js", "vendor/b.js")

    _run(str(tmp_path), "--no-default-excludes")

    assert docker.stdin() == ["dist/a.js", "keep.js", "vendor/b.js"]


def test_no_default_excludes_with_exclude(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.js", "dist/a.js", "vendor/b.js")

    _run(str(tmp_path), "--no-default-excludes", "--exclude", "vendor")

    assert docker.stdin() == ["dist/a.js", "keep.js"]


def test_no_default_excludes_still_skips_declaration_files(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.ts", "types.d.ts", "dist/a.d.mts", "dist/b.ts")

    _run(str(tmp_path), "--no-default-excludes")

    assert docker.stdin() == ["dist/b.ts", "keep.ts"]


# --- --ignore and --include --------------------------------------------------------


def test_ignore_is_repeatable(tmp_path, capsys, docker):
    _touch(tmp_path, "src/a.ts", "src/a.test.ts", "src/b.spec.js")

    _run(str(tmp_path), "--ignore", "**/*.test.ts", "--ignore", "**/*.spec.js")

    assert docker.stdin() == ["src/a.ts"]


def test_include_is_repeatable(tmp_path, capsys, docker):
    _touch(tmp_path, "src/a.ts", "lib/b.js", "scripts/c.js")

    _run(str(tmp_path), "--include", "src/**", "--include", "lib/**")

    assert docker.stdin() == ["lib/b.js", "src/a.ts"]


def test_include_and_extensions_must_both_match(tmp_path, capsys, docker):
    _touch(tmp_path, "a.js", "data.json")

    assert _run(str(tmp_path), "--include", "**/*.json") == 0

    assert docker.stdin() is None
    assert "No JavaScript/TypeScript files found for analysis." in capsys.readouterr().out


def test_include_does_not_rescue_declaration_files(tmp_path, capsys, docker):
    _touch(tmp_path, "a.ts", "types.d.ts")

    _run(str(tmp_path), "--include", "*.ts")

    assert docker.stdin() == ["a.ts"]


# --- .gitignore --------------------------------------------------------------------


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / ".gitignore").write_text("*.gen.js\ngenerated/\n")
    _touch(repo, "main.js", "skip.gen.js", "kept.gen.js", "generated/x.js")
    _git(repo, "add", "-f", "kept.gen.js")
    return repo


@needs_git
def test_gitignore_is_on_by_default(repo, capsys, docker):
    assert _run(str(repo)) == 0

    assert docker.stdin() == ["kept.gen.js", "main.js"]
    assert capsys.readouterr().err == ""


@needs_git
def test_no_gitignore_keeps_ignored_files(repo, capsys, docker):
    _run(str(repo), "--no-gitignore")

    assert docker.stdin() == ["generated/x.js", "kept.gen.js", "main.js", "skip.gen.js"]


@needs_git
def test_gitignore_applies_to_a_single_file(repo, capsys, docker):
    assert _run(str(repo / "skip.gen.js")) == 0

    assert docker.stdin() is None
    assert "No JavaScript/TypeScript files found for analysis." in capsys.readouterr().out


def test_outside_a_work_tree_nothing_is_skipped_or_printed(tmp_path, capsys, docker):
    (tmp_path / ".gitignore").write_text("*.js\n")
    _touch(tmp_path, "a.js")

    assert _run(str(tmp_path)) == 0

    assert docker.stdin() == ["a.js"]
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "git" not in captured.out.lower()


def test_missing_git_prints_nothing(tmp_path, capsys, docker, monkeypatch):
    _touch(tmp_path, "a.js")
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))

    assert _run(str(tmp_path)) == 0

    assert docker.stdin() == ["a.js"]
    assert capsys.readouterr().err == ""


# --- filter order ------------------------------------------------------------------


@needs_git
def test_filter_order_first_rejecting_step_wins(repo, capsys, docker):
    # Every candidate except main.js matches several steps; all are dropped.
    _touch(repo, "dist/a.js", "test/b.js", "lib/c.js", "lib/d.js")

    _run(
        str(repo), "--exclude", "test",
        "--ignore", "dist/**", "--ignore", "test/**", "--ignore", "lib/c.js",
        "--include", "lib/**", "--include", "generated/**",
    )

    assert docker.stdin() == ["lib/d.js"]


def test_include_does_not_rescue_excluded_directories(tmp_path, capsys, docker):
    _touch(tmp_path, "vendor/a.js", "lib/b.js")

    _run(str(tmp_path), "--include", "vendor/**", "--include", "lib/**")

    assert docker.stdin() == ["lib/b.js"]


# --- single-file <path> ------------------------------------------------------------


def test_single_file_directory_excludes_do_not_apply(tmp_path, capsys, docker):
    _touch(tmp_path, "test/a.js")

    _run(str(tmp_path / "test" / "a.js"), "--exclude", "test,a.js")

    assert docker.stdin() == ["a.js"]


@pytest.mark.parametrize(
    ("flag", "glob", "selected"),
    [
        ("--ignore", "a.js", False),
        ("--ignore", "*.ts", True),
        ("--include", "a.*", True),
        ("--include", "test/**", False),
    ],
)
def test_single_file_globs_match_the_file_name(tmp_path, capsys, docker, flag, glob, selected):
    _touch(tmp_path, "test/a.js")

    assert _run(str(tmp_path / "test" / "a.js"), flag, glob) == 0

    assert docker.stdin() == (["a.js"] if selected else None)


# --- symlinks ----------------------------------------------------------------------


def test_symlinks_inside_outside_absolute_and_dangling(tmp_path, capsys, docker):
    project = tmp_path / "project"
    _touch(tmp_path, "outside.js", "project/lib/real.js", "project/lib/abs.ts")
    (project / "rel.js").symlink_to("lib/real.js")
    (project / "abs_inside.ts").symlink_to(project / "lib" / "abs.ts")
    (project / "out.js").symlink_to(tmp_path / "outside.js")
    (project / "dangling.js").symlink_to(project / "missing.js")

    _run(str(project), "--no-default-excludes")

    assert docker.stdin() == ["lib/abs.ts", "lib/real.js"]


def test_default_excludes_constant_is_used(tmp_path, capsys, docker):
    _touch(tmp_path, "keep.js", *(f"{name}/x.js" for name in Constants.DEFAULT_EXCLUDES))

    _run(str(tmp_path), "--exclude", "extra")

    assert docker.stdin() == ["keep.js"]
