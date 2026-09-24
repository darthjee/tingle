"""reporter.py — Print the results table and summary."""

from __future__ import annotations

from pathlib import Path

from .file_analyzer import FileAnalyzer
from .palette import Palette


class Reporter:
    """Print the analysis table and summary for a set of results."""

    def __init__(self, analyzer: FileAnalyzer, target: Path, palette: Palette | None = None):
        """Store the analyzer, the reported target and the palette (default: stdout's)."""
        self._analyzer = analyzer
        self._target = target
        self._palette = palette if palette is not None else Palette()

    def report(self, results: list[tuple[Path, int]]) -> None:
        """Print the table and summary for the given (path, lines) results."""
        analyzer = self._analyzer
        target = self._target
        c = self._palette

        # Table header
        print(f"{'Status':<16} {'Lines':>10}  {'File'}")
        print(f"{'─' * 16} {'─' * 10}  {'─' * 50}")

        counts = {"ok": 0, "warn": 0, "error": 0, "critical": 0}
        total_lines = 0

        for path, lines in results:
            label, level = analyzer.classify(lines)
            try:
                display_path = str(
                    path.relative_to(target.parent)
                ) if target.is_dir() else path.name
            except ValueError:
                display_path = str(path)

            print(
                f"{c.level_color(level)}{label:<16}{c.RESET} "
                f"{analyzer.format_number(lines):>10}  {display_path}"
            )

            total_lines += lines
            counts[level] += 1

        # Summary
        print()
        print(f"{c.GRAY}{'─' * 78}{c.RESET}")
        print(
            f"{c.BOLD}Summary:{c.RESET} "
            f"{len(results)} file(s) | "
            f"{c.GREEN}{counts['ok']} OK{c.RESET} | "
            f"{c.YELLOW}{counts['warn']} WARN{c.RESET} | "
            f"{c.RED}{counts['error']} ERROR{c.RESET} | "
            f"{c.MAGENTA}{counts['critical']} CRITICAL{c.RESET}"
        )
        print(f"{c.BOLD}Total:{c.RESET} {analyzer.format_number(total_lines)} lines")
