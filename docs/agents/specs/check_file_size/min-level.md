# Spec: `--min-level` display filter

Sub-issue: #252. Shared contracts: [README.md](README.md) (flags, display vs
counting, exit codes).

## Behaviour

- `--min-level ok|warn|error|critical` (default `ok`) shows only rows whose
  level is **at or above** the given one. The order is OK < WARN < ERROR <
  CRITICAL, the same as `--fail-on`.
- It is a **display-only** filter. The summary line, the `Total:` line and the
  `--fail-on` gate still use every analysed file (README section 6).
- It is applied **before** `--top`: `--top N` shows the N largest rows left
  after `--min-level`.
- When no row passes, the table header is **not** printed. A one-line note is
  printed instead, followed by the usual summary:

  ```
  No files at or above WARN.

  ──────────────────────────────────────────── (separator)
  Summary: 12 file(s) | 12 OK | 0 WARN | 0 ERROR | 0 CRITICAL
  Total: 1,234 lines
  ```

  The note uses the level name in upper case and goes to stdout. The exit code
  is 0, unless the `--fail-on` gate fails.
- "No files found for analysis." (nothing was collected) is unchanged and
  takes priority over this note.
- An invalid value (`--min-level foo`) is a usage error: argparse `choices`,
  message on stderr, exit 1.

## Examples

| Invocation | Rows shown |
|------------|------------|
| `tingle check_file_size .` | All rows (`ok`). |
| `tingle check_file_size . --min-level warn` | WARN, ERROR and CRITICAL rows. |
| `tingle check_file_size . --min-level error --top 5` | The 5 largest ERROR/CRITICAL rows. |
| `tingle check_file_size . --min-level critical --fail-on error` | Only CRITICAL rows. Exit 2 if any file is ERROR or higher, shown or not. |

## Edge cases

- `--min-level ok` behaves exactly like not passing the flag.
- `--top 0` with `--min-level` shows every row at or above the level.
- `--top` larger than the filtered row count shows them all.
- Thresholds (`--warn`/`--error`/`--critical`) are applied first, and
  `--min-level` filters on the resulting classification.

## Technical decisions

- `FLAGS` adds `--min-level` with `choices: ["ok", "warn", "error",
  "critical"]` and `default: None`. The built-in default `ok` is applied after
  the config merge (README section 4).
- The level check reuses `FileAnalyzer.reaches(lines, level)` and
  `FileAnalyzer.LEVELS`. There is no second ordering list. `reaches(lines,
  "ok")` must be `True` for any count.
- `Reporter.report` is split so that it receives both the full results (for
  the summary and `Total:`) and the displayed rows. For example,
  `report(results, shown)`, where `shown` is `results` after `--min-level` and
  then `--top`. The same change makes `--top` stop cutting the summary
  (README section 6). The empty-row note is printed by `Reporter`, which
  needs the `min_level` name for its message.
- `executor.py` keeps evaluating the gate on the full `results`.

## Tests expected

- `test_file_analyzer.py`: `reaches(..., "ok")` is always `True`.
- `test_reporter.py`: the summary counts and total use the full results when
  fewer rows are shown; with no shown rows, it prints the note and no table
  header.
- `test_executor.py`: `--min-level` filters rows; it is applied before `--top`;
  `--top` no longer changes the summary; the gate is unaffected by
  `--min-level`; an invalid value exits 1.
