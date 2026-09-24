# Python Plan: Codacy: Method run has a cyclomatic complexity of 12 (limit is 10) (python/check_file_size/executor.py:117)

Main plan: [plan.md](plan.md)

## Overview
Reduce the cyclomatic complexity of `CheckFileSize.run()` (currently 12, Lizard limit 10) by extracting private helpers, without changing output, ordering or exit codes (0 success/help/no files, 1 errors, 2 failed `--fail-on` gate).

## Context
`run()` currently inlines: no-args help exit, path resolution/validation, exclude parsing, header printing, collection, the empty-result exit, line counting (dropping unreadable files, `lines < 0`), sorting, the `--fail-on` gate (evaluated on **all** results, before `--top`), `--top` truncation, reporting and the exit-2 decision. The list comprehension, lambda, `any()` generator and the `for`/`if` in the analysis loop all add to its score. Same approach as the earlier `python/kube/executor.py` refactors (#74, #75): small private (static) methods on the class.

## Implementation Steps

### Step 1 — Extract helpers in `executor.py`
Add private methods to `CheckFileSize` (static where they need no instance state), for example:

- `_resolve_target(path: str) -> Path` — resolve the path; if it does not exist, print the red `Error: path not found: <target>` message to stderr via `Palette(sys.stderr)` and `sys.exit(1)`.
- `_parse_excludes(raw: str) -> list[str]` — the comma split/strip/filter.
- `_print_header(out: Palette, target: Path, args: dict) -> None` — the "Analyzing:" line, thresholds line and blank line, byte-for-byte identical.
- `_analyze(analyzer: FileAnalyzer, files) -> list[tuple[Path, int]]` — count lines, drop results with `lines < 0`, sort descending by line count.
- `_gate_failed(analyzer: FileAnalyzer, results, fail_on: str | None) -> bool` — `fail_on is not None and any(analyzer.reaches(...))`.

`run()` then reads roughly: build parser → no-args help/exit 0 → `_parse` → `_resolve_target` → `Palette(sys.stdout)` → `_print_header` → collect with `FileCollector(self._parse_excludes(...), args["ext"])` → empty → message/exit 0 → `FileAnalyzer(...)` → `_analyze` → `gate_failed = self._gate_failed(...)` **before** applying `--top` → truncate when `args["top"] > 0` → `Reporter(...).report(results)` → `sys.exit(2)` if the gate failed. Keep the order of side effects identical (path error before header; header before "No files found"). Update the class docstring only if needed; keep docstrings compliant with the repo's ruff/pydocstyle config (summary on the first line, D212).

### Step 2 — Tests
All existing tests in `python/tests/check_file_size/test_executor.py` must pass unchanged (they cover help, path-not-found, no files, reporting, `--top`, plain output, usage errors, and every `--fail-on` case including the offender hidden by `--top`). Add focused unit tests for the new pure helpers, e.g. `_parse_excludes` (whitespace, empty entries), `_analyze` (sorting, dropping `-1` counts — stub/monkeypatch `count_lines` or use unreadable files) and `_gate_failed` (`None`, below, at and above the level).

## Files to Change
- `python/check_file_size/executor.py` — extract helpers, slim down `run()`.
- `python/tests/check_file_size/test_executor.py` — add helper unit tests; existing tests untouched.

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)
- Optional local complexity check: `lizard -C 10 python/check_file_size/executor.py` (if lizard is installed) to confirm no function exceeds CCN 10.

## Notes
- Pure refactor: no CLI, help text, output or exit-code changes; no docs/guides update needed.
- Do not move the `--fail-on` evaluation after `--top` truncation — `test_run_fail_on_still_fails_when_offender_hidden_by_top` guards this.
- Avoid pushing the new complexity into another method above 10; each helper should be trivially small.
