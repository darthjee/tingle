"""skip_checks.py — Determine whether a file should be skipped from analysis."""

from __future__ import annotations

from pathlib import Path

from .constants import Constants


class SkipChecks:
    """Determine whether a file should be skipped from analysis."""

    @staticmethod
    def is_binary_file(path: Path) -> bool:
        """Check if a file is binary by extension or content."""
        # 1. Known binary extension
        if path.suffix.lower() in Constants.BINARY_EXTENSIONS:
            return True

        # 2. Content-based detection — read first 1024 bytes
        try:
            with open(path, "rb") as f:
                chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
            try:
                chunk.decode("utf-8")
            except UnicodeDecodeError:
                return True
        except (OSError, PermissionError):
            return True

        return False
