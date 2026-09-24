"""file_analyzer.py — Count lines and classify files by threshold."""

from __future__ import annotations

from pathlib import Path


class FileAnalyzer:
    """Count lines and classify files by threshold."""

    def __init__(self, warn: int, error: int, critical: int):
        """Store the warn/error/critical line-count thresholds."""
        self._warn = warn
        self._error = error
        self._critical = critical

    @staticmethod
    def count_lines(path: Path) -> int:
        """Count the number of lines in a text file. Returns -1 on error."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return sum(1 for _ in f)
        except (OSError, PermissionError):
            return -1

    def classify(self, lines: int) -> tuple[str, str]:
        """Return (label, level) based on line count and thresholds.

        `level` is one of `ok`, `warn`, `error` or `critical`; colours are
        resolved from it by `Palette.level_color`.
        """
        if lines >= self._critical:
            return ("🟣 CRITICAL", "critical")
        elif lines >= self._error:
            return ("🔴 ERROR", "error")
        elif lines >= self._warn:
            return ("⚠️  WARN", "warn")
        else:
            return ("✅ OK", "ok")

    @staticmethod
    def format_number(n: int) -> str:
        """Format number with thousands separator."""
        return f"{n:,}".replace(",", ".")
