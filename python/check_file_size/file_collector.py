"""file_collector.py — Walk paths recursively, applying exclusions and filters."""

from __future__ import annotations

from pathlib import Path

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
    ):
        """Store the resolved filters.

        `excludes` and `extensions` are case-insensitive (`extensions=None`: no
        filter). `ignore` / `include` are glob lists matched against the path
        relative to the target (`None`: no globs).
        """
        self._exclude_set = {e.lower() for e in excludes}
        self._ext_set = {e.lower() for e in extensions} if extensions else None
        self._ignore = GlobMatcher(ignore or [])
        self._include = GlobMatcher(include or [])

    def collect(self, target: Path) -> list[Path]:
        """Collect all analyzable files from a file or directory path."""
        if target.is_file():
            return [target] if self._accepts(target, target.name) else []

        if not target.is_dir():
            return []

        files = []
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            if self._is_excluded(path):
                continue
            if self._accepts(path, path.relative_to(target).as_posix()):
                files.append(path)

        return files

    def _accepts(self, path: Path, rel: str) -> bool:
        """Apply the glob, extension and binary filters, in that order, to one file."""
        if self._ignore.matches(rel):
            return False
        if self._include and not self._include.matches(rel):
            return False
        if self._ext_set and path.suffix.lower() not in self._ext_set:
            return False
        return not SkipChecks.is_binary_file(path)

    def _is_excluded(self, path: Path) -> bool:
        """Check if any path component matches an exclusion entry."""
        return any(
            part.lower() in self._exclude_set
            for part in path.parts
        )
