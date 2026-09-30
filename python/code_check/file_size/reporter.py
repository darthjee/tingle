"""reporter.py — Print the results table and summary."""

from __future__ import annotations

from pathlib import Path

from code_check.palette import Palette

from .file_analyzer import FileAnalyzer


class Reporter:
    """Print the analysis table and summary for a set of results."""

    def __init__(self, analyzer: FileAnalyzer, target: Path, palette: Palette | None = None):
        """Store the analyzer, the reported target and the palette (default: stdout's)."""
        self._analyzer = analyzer
        self._target = target
        self._palette = palette if palette is not None else Palette()

    def report(
        self,
        results: list[tuple[Path, int]],
        shown: list[tuple[Path, int]] | None = None,
        min_level: str = "ok",
    ) -> None:
        """Print the table for `shown` and the summary for every entry in `results`.

        `shown` defaults to `results`. When it is empty (and `results` is not),
        the table header is replaced by a `No files at or above <LEVEL>.` note.
        """
        if shown is None:
            shown = results

        if shown or not results:
            self._print_table(shown)
        else:
            print(f"No files at or above {min_level.upper()}.")

        self._print_summary(results)

    def _display_path(self, path: Path) -> str:
        """Return `path` relative to the target's parent (or its name for a file)."""
        target = self._target
        try:
            return str(path.relative_to(target.parent)) if target.is_dir() else path.name
        except ValueError:
            return str(path)

    def _print_table(self, rows: list[tuple[Path, int]]) -> None:
        """Print the table header and one row per (path, lines) entry."""
        analyzer = self._analyzer
        c = self._palette

        print(f"{'Status':<16} {'Lines':>10}  {'File'}")
        print(f"{'─' * 16} {'─' * 10}  {'─' * 50}")

        for path, lines in rows:
            label, level = analyzer.classify(lines)
            print(
                f"{c.level_color(level)}{label:<16}{c.RESET} "
                f"{analyzer.format_number(lines):>10}  {self._display_path(path)}"
            )

    def _print_summary(self, results: list[tuple[Path, int]]) -> None:
        """Print the separator, per-level counts and total lines for `results`."""
        analyzer = self._analyzer
        c = self._palette

        counts = {level: 0 for level in FileAnalyzer.LEVELS}
        total_lines = 0
        for _path, lines in results:
            _label, level = analyzer.classify(lines)
            counts[level] += 1
            total_lines += lines

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
