# Report table and summary
Add `python/code_check/js_complexity/reporter.py`: a `Reporter(analyzer, target, root, out)` mirroring `rubycritic/reporter.py`, implementing spec §6. It does **not** print the header (`DockerCheck._print_header` already prints `Analyzing:`, `Thresholds:` and `Image:`).

- `display_path(line)` follows rubycritic's rule: the path relative to the target's parent for a directory, the file name for a single file.
- Table header and separator: exactly the spec's f-string and the `─` widths 16/5/5/5/17/50.
- Level row:
  - the label, padded to 16 and coloured with `Palette.level_color`;
  - the score as `{s:>5.1f}`;
  - `cyclo` and `lines` as `>5` ints, or `-` for dropped or refused files;
  - `assessment` as `<17`, or `-`;
  - the file.
- `⛔ PARSE` rows: gray, `-` in every value column.
- Order:
  - level rows by `s` descending, ties by sent line ascending;
  - then `PARSE` rows by sent line.
- Filters:
  - `--min-level` first, then `--top N` (N > 0) on the level rows only;
  - `PARSE` rows are always shown and never counted by `--top`;
  - when no row is left at all, print `No files at or above <LEVEL>.`.
- Summary (always over every selected file):
  - the 78-wide gray rule;
  - `Summary: <N> file(s) | <a> OK | <b> WARN | <c> ERROR | <d> CRITICAL`, with ` | <k> skipped (parse error)` (gray) only when k > 0;
  - `FTA score: avg <avg> | max <max>` with 2 decimals over the level rows, or `FTA score: n/a` when there are none.
- Classify with `FileAnalyzer(warn, error, critical).classify(s)`. Check that `classify` and `reaches` work with float values. They are typed as `int` but are plain comparisons.

Tests (`test_reporter.py`, plain-text `Palette`):
- the layout against the spec §6 full example;
- the sort and ties;
- `--top` and `--min-level`, including the `No files at or above` message;
- `PARSE` rows, dropped and refused rows;
- the summary with and without the skipped part, and `n/a`;
- each level boundary on the rounded score.

## Files to Change
- `python/code_check/js_complexity/reporter.py`: new.
- `python/tests/code_check/js_complexity/test_reporter.py`: new.
