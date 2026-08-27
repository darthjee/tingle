"""file_analyzer.py — Count lines and classify files by threshold."""

from __future__ import annotations

from pathlib import Path

from .constants import Constants


class FileAnalyzer:
    """Count lines and classify files by threshold."""

    def __init__(self, warn: int, error: int, critical: int):
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
        """Return (label, color) based on line count and thresholds."""
        if lines >= self._critical:
            return ("🟣 CRITICAL", Constants.MAGENTA + Constants.BOLD)
        elif lines >= self._error:
            return ("🔴 ERROR", Constants.RED + Constants.BOLD)
        elif lines >= self._warn:
            return ("⚠️  WARN", Constants.YELLOW)
        else:
            return ("✅ OK", Constants.GREEN)

    @staticmethod
    def format_number(n: int) -> str:
        """Format number with thousands separator."""
        return f"{n:,}".replace(",", ".")
