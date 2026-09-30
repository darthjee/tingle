"""Unit and integration tests for code_check.file_size.git_ignore."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_check.file_size import git_ignore
from code_check.file_size.git_ignore import GitIgnore, GitIgnored

EXPECTED_ARGS = [
    "ls-files",
    "--others",
    "--ignored",
    "--exclude-standard",
    "--directory",
    "-z",
]


def _fake_run(calls, returncode=0, stdout=b""):
    def run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=b"")

    return run


class TestParse:
    """GitIgnore.parse / GitIgnored.contains."""

    def test_splits_files_and_directories(self, tmp_path):
        ignored = GitIgnore.parse(tmp_path, b"debug.log\0build/\0sub/out.txt\0\0")
        assert ignored.files == {tmp_path / "debug.log", tmp_path / "sub" / "out.txt"}
        assert ignored.dirs == [tmp_path / "build"]

    def test_empty_output_ignores_nothing(self, tmp_path):
        ignored = GitIgnore.parse(tmp_path, b"")
        assert ignored.files == set()
        assert ignored.dirs == []

    def test_contains(self, tmp_path):
        ignored = GitIgnore.parse(tmp_path, b"debug.log\0build/\0")
        assert ignored.contains(tmp_path / "debug.log")
        assert ignored.contains(tmp_path / "build" / "deep" / "a.js")
        assert not ignored.contains(tmp_path / "main.py")
        assert not ignored.contains(tmp_path / "buildx" / "a.js")

    def test_contains_on_empty_set(self, tmp_path):
        assert not GitIgnored(set(), []).contains(tmp_path / "a.py")


class TestIgnoredPathsMocked:
    """GitIgnore.ignored_paths with subprocess.run mocked."""

    def test_calls_git_once_with_exact_args(self, tmp_path, monkeypatch):
        calls = []
        monkeypatch.setattr(
            git_ignore.subprocess, "run", _fake_run(calls, stdout=b"a.log\0dist/\0")
        )

        ignored = GitIgnore.ignored_paths(tmp_path)

        assert len(calls) == 1
        args, kwargs = calls[0]
        assert args == ["git", "-C", str(tmp_path), *EXPECTED_ARGS]
        assert kwargs["capture_output"] is True
        assert kwargs.get("check") in (None, False)
        assert "shell" not in kwargs
        assert ignored.contains(tmp_path / "a.log")
        assert ignored.contains(tmp_path / "dist" / "x.js")

    def test_none_when_git_missing(self, tmp_path, monkeypatch):
        def run(*_args, **_kwargs):
            raise FileNotFoundError("git")

        monkeypatch.setattr(git_ignore.subprocess, "run", run)
        assert GitIgnore.ignored_paths(tmp_path) is None

    def test_none_on_os_error(self, tmp_path, monkeypatch):
        def run(*_args, **_kwargs):
            raise PermissionError("denied")

        monkeypatch.setattr(git_ignore.subprocess, "run", run)
        assert GitIgnore.ignored_paths(tmp_path) is None

    def test_none_on_non_zero_exit(self, tmp_path, monkeypatch):
        calls = []
        monkeypatch.setattr(
            git_ignore.subprocess, "run", _fake_run(calls, returncode=128, stdout=b"a.log\0")
        )
        assert GitIgnore.ignored_paths(tmp_path) is None


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
class TestIgnoredPathsIntegration:
    """GitIgnore.ignored_paths against a real temporary repository."""

    @pytest.fixture(autouse=True)
    def _isolate_git(self, monkeypatch, tmp_path):
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
        monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
        monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))

    @staticmethod
    def _git(repo: Path, *args: str) -> None:
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)

    @pytest.fixture
    def repo(self, tmp_path):
        repo = (tmp_path / "repo").resolve()
        repo.mkdir()
        self._git(repo, "init", "-q")
        (repo / ".gitignore").write_text("*.log\nnode_modules/\n")
        (repo / "main.py").write_text("print('hi')\n")
        (repo / "debug.log").write_text("noise\n")
        (repo / "keep.log").write_text("tracked\n")
        (repo / "node_modules" / "pkg").mkdir(parents=True)
        (repo / "node_modules" / "pkg" / "index.js").write_text("x\n")
        (repo / "sub").mkdir()
        (repo / "sub" / ".gitignore").write_text("*.tmp\n")
        (repo / "sub" / "scratch.tmp").write_text("tmp\n")
        (repo / "top.tmp").write_text("not ignored at the top\n")
        self._git(repo, "add", "-f", "keep.log")
        return repo

    def test_ignored_untracked_file_is_listed(self, repo):
        ignored = GitIgnore.ignored_paths(repo)
        assert ignored.contains(repo / "debug.log")

    def test_tracked_file_matching_gitignore_is_not_listed(self, repo):
        ignored = GitIgnore.ignored_paths(repo)
        assert not ignored.contains(repo / "keep.log")
        assert not ignored.contains(repo / "main.py")

    def test_nested_gitignore_is_respected(self, repo):
        ignored = GitIgnore.ignored_paths(repo)
        assert ignored.contains(repo / "sub" / "scratch.tmp")
        assert not ignored.contains(repo / "top.tmp")

    def test_ignored_directory_is_a_prefix(self, repo):
        ignored = GitIgnore.ignored_paths(repo)
        assert repo / "node_modules" in ignored.dirs
        assert ignored.contains(repo / "node_modules" / "pkg" / "index.js")

    def test_subdirectory_honours_parent_gitignore(self, repo):
        (repo / "sub" / "inner.log").write_text("x\n")
        ignored = GitIgnore.ignored_paths(repo / "sub")
        assert ignored.contains(repo / "sub" / "inner.log")
        assert ignored.contains(repo / "sub" / "scratch.tmp")

    def test_non_repository_returns_none(self, tmp_path):
        plain = tmp_path / "plain"
        plain.mkdir()
        assert GitIgnore.ignored_paths(plain) is None
