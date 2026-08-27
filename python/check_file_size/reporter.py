#!/usr/bin/env python3
"""reporter.py — Print the results table and summary."""

from __future__ import annotations

from pathlib import Path

from .constants import Constants
from .file_analyzer import FileAnalyzer


class Reporter:
    """Print the analysis table and summary for a set of results."""

    def __init__(self, analyzer: FileAnalyzer, target: Path):
        self._analyzer = analyzer
        self._target = target

    def report(self, results: list[tuple[Path, int]]) -> None:
        """Print the table and summary for the given (path, lines) results."""
        analyzer = self._analyzer
        target = self._target

        # Table header
        print(f"{'Status':<16} {'Lines':>10}  {'File'}")
        print(f"{'─' * 16} {'─' * 10}  {'─' * 50}")

        counts = {"OK": 0, "WARN": 0, "ERROR": 0, "CRITICAL": 0}
        total_lines = 0

        for path, lines in results:
            label, color = analyzer.classify(lines)
            try:
                display_path = str(
                    path.relative_to(target.parent)
                ) if target.is_dir() else path.name
            except ValueError:
                display_path = str(path)

            print(f"{color}{label:<16}{Constants.RESET} {analyzer.format_number(lines):>10}  {display_path}")

            total_lines += lines
            if "OK" in label:
                counts["OK"] += 1
            elif "WARN" in label:
                counts["WARN"] += 1
            elif "ERROR" in label:
                counts["ERROR"] += 1
            elif "CRITICAL" in label:
                counts["CRITICAL"] += 1

        # Summary
        print()
        print(f"{Constants.GRAY}{'─' * 78}{Constants.RESET}")
        print(
            f"{Constants.BOLD}Summary:{Constants.RESET} "
            f"{len(results)} file(s) | "
            f"{Constants.GREEN}{counts['OK']} OK{Constants.RESET} | "
            f"{Constants.YELLOW}{counts['WARN']} WARN{Constants.RESET} | "
            f"{Constants.RED}{counts['ERROR']} ERROR{Constants.RESET} | "
            f"{Constants.MAGENTA}{counts['CRITICAL']} CRITICAL{Constants.RESET}"
        )
        print(f"{Constants.BOLD}Total:{Constants.RESET} {analyzer.format_number(total_lines)} lines")
