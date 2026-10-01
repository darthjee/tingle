"""file_collector.py — Walk paths recursively, applying exclusions and filters."""

from __future__ import annotations

from pathlib import Path

from .git_ignore import GitIgnore, GitIgnored
from .glob_matcher import GlobMatcher
from .skip_checks import SkipChecks


class FileCollector:
    """Walk paths recursively, applying exclusions and filters."""

    def __init__(
        self,
        excludes: list[str],
        extensions: list[str] | None,
        *,
        ignore: list[str] | None = None,
        include: list[str] | None = None,
        gitignore: bool = True,
        binary_check: bool = True,
    ):
        """Store the resolved filters.

        `excludes` are whole path-component names matched, case-insensitively,
        against the path relative to the target (never applied when the target
        is a single file). `extensions` are case-insensitive (`extensions=None`:
        no filter). `ignore` / `include` are glob lists matched against the path
        relative to the target (`None`: no globs). `gitignore` skips the untracked
        files git ignores when the target is inside a work tree (silently a no-op
        when git is missing, the target is not in a work tree or git fails).
        `binary_check` skips binary files (by extension or content); turn it off
        to keep every file that passes the other filters.
        """
        self._exclude_set = {e.lower() for e in excludes}
        self._ext_set = {e.lower() for e in extensions} if extensions else None
        self._ignore = GlobMatcher(ignore or [])
        self._include = GlobMatcher(include or [])
        self._gitignore = gitignore
        self._binary_check = binary_check

    def collect(self, target: Path) -> list[Path]:
        """Collect all analyzable files from a file or directory path."""
        if target.is_file():
            return self._collect_file(target)

        if not target.is_dir():
            return []

        root = target.resolve()
        ignored = self._git_ignored(root)
        files = []
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(target)
            if self._is_excluded(rel):
                continue
            if self._is_git_ignored(ignored, root / rel):
                continue
            if self._accepts(path, rel.as_posix()):
                files.append(path)

        return files

    def _collect_file(self, target: Path) -> list[Path]:
        """Collect a single-file target (git runs from its parent directory)."""
        parent = target.parent.resolve()
        if self._is_git_ignored(self._git_ignored(parent), parent / target.name):
            return []
        return [target] if self._accepts(target, target.name) else []

    def _git_ignored(self, root: Path) -> GitIgnored | None:
        """Ask git once for the ignored paths under `root` (`None` when disabled or unknown)."""
        if not self._gitignore:
            return None
        return GitIgnore.ignored_paths(root)

    @staticmethod
    def _is_git_ignored(ignored: GitIgnored | None, path: Path) -> bool:
        """Check if the resolved `path` is in git's ignored set (`None`: nothing ignored)."""
        return ignored is not None and ignored.contains(path)

    def _accepts(self, path: Path, rel: str) -> bool:
        """Apply the glob, extension and (optional) binary filters, in that order, to one file."""
        if self._ignore.matches(rel):
            return False
        if self._include and not self._include.matches(rel):
            return False
        if self._ext_set and path.suffix.lower() not in self._ext_set:
            return False
        return not (self._binary_check and SkipChecks.is_binary_file(path))

    def _is_excluded(self, rel: Path) -> bool:
        """Check if any component of `rel` (relative to the target) is excluded."""
        return any(
            part.lower() in self._exclude_set
            for part in rel.parts
        )
