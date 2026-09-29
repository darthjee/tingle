# Python Plan: check_file_size: add --min-level display filter

Main plan: [plan.md](plan.md)

## Shared contracts

- Produce `--min-level ok|warn|error|critical`. Default when omitted is `ok`. An invalid value exits `1` through the existing `_parse` remap.
- The filter is applied before `--top`. The summary, `Total:` and the gate use the full results.
- When no row passes, print `No files at or above <LEVEL>.` in place of the table, then the summary.

## Steps

- [01 — Add the flag and default resolution](python/01-add-flag.md)
- [02 — Split Reporter into full results vs shown rows](python/02-split-reporter.md)
- [03 — Filter and cut rows in the executor](python/03-filter-in-executor.md)
- [04 — Tests](python/04-tests.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)

## Notes
- Config loading (#253) is not merged. Use `default: None` in `FLAGS` and resolve `None` → `"ok"` in the executor, so #253 can add the config value between CLI and the built-in default.
- Keep `run()` below the cyclomatic complexity limit (see #202). Move the display selection into a small helper such as `_select_shown`.
- `test_run_applies_top_flag_to_limit_results` checks that hidden rows are absent. That still holds, but review any test that asserts summary counts together with `--top`.
