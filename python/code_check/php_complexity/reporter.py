"""reporter.py — Print the php_complexity (PDepend) results table and summary.

Mirrors `code_check.js_complexity.reporter.Reporter`: one row per file,
coloured by level on the file's total CCN, sorted by CCN (highest first, ties
by sent line), then the `⛔ PARSE` rows sorted by sent line. `--min-level`
and `--top` only filter the level rows; the summary always counts every
file. Files without PDepend data (no class, trait or function, or a line the
image refused) show CCN `0` and `-` for the rest. `Max`, `NPath`, `MI` and
`Lines` are information only.
With `details` set, each shown level row is followed by dim lines for its
most complex functions and methods (from the same PDepend run), sorted by
CCN (highest first, ties by line then name); never under PARSE rows. A row
with no per-function data (`functions` is `None`, for example a refused line
or an image older than #351) gets one dim `(per-function data unavailable)`
note instead; a file with no counted function or method (`[]`) gets nothing.
Function lines are information only: they never change a level, the summary
or the gate.
The header is printed by `DockerCheck._print_header`.
"""

from __future__ import annotations

from pathlib import Path

from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Palette
from code_check.php_complexity.output_parser import FileResult, ParsedOutput

PARSE_LABEL = "⛔ PARSE"


class Reporter:
    """Print the analysis table and summary for parsed PDepend output."""

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
        """Sort results by total CCN (highest first), ties by sent line (ascending)."""
        return sorted(results.items(), key=lambda item: (-item[1].score, item[0]))

    def select_shown(
        self, rows: list[tuple[str, FileResult]], min_level: str, top: int
    ) -> list[tuple[str, FileResult]]:
        """Keep the rows at `min_level` or higher, then the first `top` (when > 0)."""
        shown = [r for r in rows if self._analyzer.reaches(r[1].score, min_level)]
        return shown[:top] if top > 0 else shown

    def report(
        self,
        parsed: ParsedOutput,
        min_level: str = "ok",
        top: int = 0,
        details: int | None = None,
    ) -> None:
        """Print the table (or the empty-filter note) and the summary.

        `details` is the number of functions and methods listed under each
        shown level row (`0` = all, `None` = no function lines).
        """
        rows = self.sort_rows(parsed.results)
        shown = self.select_shown(rows, min_level, top)
        parse_rows = sorted(parsed.parse_errors)

        if shown or parse_rows:
            self._print_table(shown, parse_rows, details)
        else:
            print(f"No files at or above {min_level.upper()}.")

        self._print_summary(rows, len(parse_rows))

    @staticmethod
    def select_functions(functions: list[dict], details: int) -> list[dict]:
        """Sort units by CCN (highest first), then line, then name; keep `details`.

        All of them are kept when `details` is 0.
        """
        ordered = sorted(functions, key=lambda f: (-f["ccn"], f["line"], f["name"]))
        return ordered[:details] if details > 0 else ordered

    def _print_functions(self, line: str, result: FileResult, details: int) -> None:
        """Print the dim function and method lines for a row, or the unavailable note."""
        c = self._palette
        if result.functions is None:
            print(f"{c.DIM}{'':<16} (per-function data unavailable){c.RESET}")
            return
        path = self.display_path(line)
        for f in self.select_functions(result.functions, details):
            print(
                f"{c.DIM}{'':<16} ccn {f['ccn']:>3}  npath {f['npath']:>7}  "
                f"{f['name']}  ({path}:{f['line']}){c.RESET}"
            )

    @staticmethod
    def _value(value: int | None) -> str:
        """Return a column value as text, `-` when PDepend has no data."""
        return "-" if value is None else str(value)

    @staticmethod
    def _mi(value: float | None) -> str:
        """Return the lowest maintainability index rounded to an integer, `-` when absent."""
        return "-" if value is None else format(value, ".0f")

    def _print_table(
        self,
        rows: list[tuple[str, FileResult]],
        parse_rows: list[str],
        details: int | None = None,
    ) -> None:
        """Print the header, the level rows (with their function lines) and the PARSE rows."""
        c = self._palette
        print(
            f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  File"
        )
        print(f"{'─' * 16} {'─' * 5}  {'─' * 5}  {'─' * 7}  {'─' * 5}  {'─' * 5}  {'─' * 50}")

        for line, result in rows:
            label, level = self._analyzer.classify(result.score)
            print(
                f"{c.level_color(level)}{label:<16}{c.RESET} "
                f"{result.score:>5}  {self._value(result.max_ccn):>5}  "
                f"{self._value(result.max_npath):>7}  {self._mi(result.min_mi):>5}  "
                f"{self._value(result.lloc):>5}  {self.display_path(line)}"
            )
            if details is not None:
                self._print_functions(line, result, details)
        for line in parse_rows:
            print(
                f"{c.GRAY}{PARSE_LABEL:<16}{c.RESET} "
                f"{'-':>5}  {'-':>5}  {'-':>7}  {'-':>5}  {'-':>5}  {self.display_path(line)}"
            )

    def _print_summary(self, rows: list[tuple[str, FileResult]], skipped: int) -> None:
        """Print the separator, the per-level counts and the CCN line."""
        c = self._palette
        counts = {level: 0 for level in FileAnalyzer.LEVELS}
        for _line, result in rows:
            _label, level = self._analyzer.classify(result.score)
            counts[level] += 1

        suffix = f" {c.GRAY}| {skipped} skipped (parse error){c.RESET}" if skipped else ""

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
        print(f"{c.BOLD}CCN:{c.RESET} {self.score_line(rows)}")

    @staticmethod
    def score_line(rows: list[tuple[str, FileResult]]) -> str:
        """Return `avg X | max Y` over the level rows (2 decimals), or `n/a` when none."""
        if not rows:
            return "n/a"
        scores = [result.score for _line, result in rows]
        return f"avg {sum(scores) / len(scores):.2f} | max {max(scores):.2f}"
