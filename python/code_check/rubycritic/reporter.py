"""reporter.py — Print the RubyCritic results table and summary.

Mirrors `code_check.file_size.reporter.Reporter`: one row per file, coloured
by level, sorted by complexity (highest first, ties by path), then the
`⛔ PARSE` rows for the files that could not be parsed. `--min-level` and
`--top` only filter the level rows; the summary always counts every file.
"""

from __future__ import annotations

from pathlib import Path

from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Palette
from code_check.rubycritic.output_parser import FileResult, ParsedOutput

PARSE_LABEL = "⛔ PARSE"


class Reporter:
    """Print the analysis table and summary for parsed RubyCritic output."""

    def __init__(
        self,
        analyzer: FileAnalyzer,
        target: Path,
        root: Path,
        palette: Palette | None = None,
    ):
        """Store the analyzer, the reported target, the mount root and the palette."""
        self._analyzer = analyzer
        self._target = target
        self._root = root
        self._palette = palette if palette is not None else Palette()

    def display_path(self, line: str) -> str:
        """Return a sent line as shown: relative to the target's parent, or the file name."""
        if not self._target.is_dir():
            return Path(line).name
        return str((self._root / line).relative_to(self._target.parent))

    @staticmethod
    def sort_rows(results: dict[str, FileResult]) -> list[tuple[str, FileResult]]:
        """Sort results by complexity (highest first), ties by path (ascending)."""
        return sorted(results.items(), key=lambda item: (-item[1].complexity, item[0]))

    def select_shown(
        self, rows: list[tuple[str, FileResult]], min_level: str, top: int
    ) -> list[tuple[str, FileResult]]:
        """Keep the rows at `min_level` or higher, then the first `top` (when > 0)."""
        shown = [r for r in rows if self._analyzer.reaches(r[1].complexity, min_level)]
        return shown[:top] if top > 0 else shown

    def report(self, parsed: ParsedOutput, min_level: str = "ok", top: int = 0) -> None:
        """Print the table (or the empty-filter note) and the summary."""
        rows = self.sort_rows(parsed.results)
        shown = self.select_shown(rows, min_level, top)
        parse_rows = sorted(parsed.parse_errors)

        if shown or parse_rows:
            self._print_table(shown, parse_rows)
        else:
            print(f"No files at or above {min_level.upper()}.")

        self._print_summary(rows, len(parse_rows), parsed.score)

    def _print_table(self, rows: list[tuple[str, FileResult]], parse_rows: list[str]) -> None:
        """Print the header, the level rows and the PARSE rows."""
        c = self._palette
        print(
            f"{'Status':<16} {'Complexity':>10}  {'Rating':<6}  {'Smells':>6}  "
            f"{'Duplication':>11}  File"
        )
        print(f"{'─' * 16} {'─' * 10}  {'─' * 6}  {'─' * 6}  {'─' * 11}  {'─' * 50}")

        for line, result in rows:
            label, level = self._analyzer.classify(result.complexity)
            print(
                f"{c.level_color(level)}{label:<16}{c.RESET} "
                f"{result.complexity:>10.2f}  {result.rating:<6}  {result.smells:>6}  "
                f"{round(result.duplication):>11}  {self.display_path(line)}"
            )
        for line in parse_rows:
            print(
                f"{c.GRAY}{PARSE_LABEL:<16}{c.RESET} "
                f"{'-':>10}  {'-':<6}  {'-':>6}  {'-':>11}  {self.display_path(line)}"
            )

    def _print_summary(
        self, rows: list[tuple[str, FileResult]], skipped: int, score: float | None
    ) -> None:
        """Print the separator, the per-level counts and RubyCritic's score."""
        c = self._palette
        counts = {level: 0 for level in FileAnalyzer.LEVELS}
        for _line, result in rows:
            _label, level = self._analyzer.classify(result.complexity)
            counts[level] += 1

        suffix = f" {c.GRAY}| {skipped} skipped (parse error){c.RESET}" if skipped else ""
        shown_score = "n/a" if score is None else f"{score:.2f}/100"

        print()
        print(f"{c.GRAY}{'─' * 78}{c.RESET}")
        print(
            f"{c.BOLD}Summary:{c.RESET} "
            f"{len(rows) + skipped} file(s) | "
            f"{c.GREEN}{counts['ok']} OK{c.RESET} | "
            f"{c.YELLOW}{counts['warn']} WARN{c.RESET} | "
            f"{c.RED}{counts['error']} ERROR{c.RESET} | "
            f"{c.MAGENTA}{counts['critical']} CRITICAL{c.RESET}"
            f"{suffix}"
        )
        print(f"{c.BOLD}Score:{c.RESET} {shown_score} (RubyCritic)")
