# Python Plan: code_check: clean up stale check_file_size mentions in docs and tests

Main plan: [plan.md](plan.md)

## Shared contracts

None. Do not change the `CheckFileSize` class name, `LEGACY_CONFIG_SECTION`, the
`python/check_file_size/` shim, or the legacy-section tests in
`python/tests/code_check/file_size/test_executor_config.py`.

## Implementation Steps

### Step 1 — Use `file_size` as the example section in test_config.py

`python/tests/code_check/test_config.py` tests the generic
`code_check.config.load_section` / `load_sections`. These tests don't care what
the section is called, but they use `"check_file_size"` everywhere, and that is
now the legacy key. Replace every `"check_file_size"` in this file with
`"file_size"`: the JSON keys, the `load_section(...)` arguments, and the expected
error messages such as `"'file_size' must be an object"`. Nothing else in these
tests changes.

### Step 2 — Rename the subcommand-table test

In `python/tests/code_check/test_executor.py`, rename
`test_subcommands_maps_file_size_to_check_file_size` to
`test_subcommands_maps_file_size_to_executor`. The body stays the same.

## Files to Change

- `python/tests/code_check/test_config.py` — use `"file_size"` as the section name.
- `python/tests/code_check/test_executor.py` — rename one test.

## CI Checks

- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`, coverage stays at or above 75%)

## Notes

- Check the parametrised error-message cases (around lines 83–85) after the
  rename. The messages come from `load_section` and include the section name
  passed in, so they will read `'file_size' must be an object`.
