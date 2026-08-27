"""file_collector.py — Walk paths recursively, applying exclusions and filters."""

from __future__ import annotations

from pathlib import Path

from .skip_checks import SkipChecks


class FileCollector:
    """Walk paths recursively, applying exclusions and filters."""

    def __init__(self, excludes: list[str], extensions: list[str] | None):
        self._exclude_set = {e.lower() for e in excludes}
        self._ext_set = {e.lower() for e in extensions} if extensions else None

    def collect(self, target: Path) -> list[Path]:
        """Collect all analyzable files from a file or directory path."""
        if target.is_file():
            if not SkipChecks.is_binary_file(target):
                return [target]
            return []

        if not target.is_dir():
            return []

        files = []
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            if self._is_excluded(path):
                continue
            if self._ext_set and path.suffix.lower() not in self._ext_set:
                continue
            if SkipChecks.is_binary_file(path):
                continue
            files.append(path)

        return files

    def _is_excluded(self, path: Path) -> bool:
        """Check if any path component matches an exclusion entry."""
        return any(
            part.lower() in self._exclude_set
            for part in path.parts
        )
