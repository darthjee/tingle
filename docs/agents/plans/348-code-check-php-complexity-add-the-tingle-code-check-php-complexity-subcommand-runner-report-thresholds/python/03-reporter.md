# Reporter
Implement `reporter.py` per cli.md §6, mirroring `js_complexity`'s `Reporter`:

- The header: `Analyzing:`, the `Image:` line and `Thresholds:`.
- The table header: `f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  File"`. Value formats and `-` placeholders follow the §6 table; `MI` is `format(min_mi, ".0f")`.
- Sorting: by CCN, highest first, with the ties as in §6. `PARSE` rows (gray `⛔ PARSE`, `-` in every column) come last, in sent order.
- Display filters: `--min-level` first, then `--top`. `PARSE` rows are always shown and are not counted by `--top`. When no level row is left, print `No files at or above <LEVEL>.`
- The summary counts every selected file (`skipped (parse error)` only when there is at least one), then `CCN: avg | max` over the level rows, or `CCN: n/a`.

Add `test_reporter.py`, covering the §11 report list and the exact output of the §6 full example.

## Files to Change
- `python/code_check/php_complexity/reporter.py` — new
- `python/tests/code_check/php_complexity/test_reporter.py` — new
