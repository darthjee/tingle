# Python Plan: code_check js_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Consumes `files[].duplication` (`{"lines": int}` or `null`) and path-less `{"tool": "jscpd", "message"}` warnings, as in [plan.md](plan.md#shared-contracts). `output_parser.py` already validates both (`_valid_duplication`, `WARNING_TOOLS`) and keeps `FileResult.duplication` and `ParsedOutput.warnings`, so no parser change is expected.

## Implementation Steps

### Step 1 — `Dup` column in the reporter
In `Reporter._print_table`, add `Dup` between `Lines` and `Assessment` using the exact header and separator from spec section 4. For a level row, show `result.duplication["lines"]` as `{:>5}`, or `-` when `duplication` is `None`. Add one more `-` column to the `PARSE` rows. The summary, the sorting and the classification are unchanged. Update the module docstring.

### Step 2 — jscpd warning, help text and tests
- In `JsComplexityExecutor._print_warnings`, for each warning with `tool == "jscpd"` and no `path`, call `_warn(f"jscpd failed in {image}; duplication data is not available: {message}")`. This needs the image name: pass it in, or print from `_execute`. Keep the existing order (refused lines, then parse errors), and print the jscpd warning first or last consistently. The exit code is unchanged.
- In the `executor.py` module docstring (the long help), say that `Dup` (the lines in exact clones found by jscpd among the selected files) is information only.
- Tests:
  - `test_reporter.py`: the header and separator with `Dup`; a row with a number, with `0` and with `null` → `-`; a `PARSE` row with `-`; update the full-example layout to match spec section 4.
  - `test_executor.py`: the jscpd warning text on stderr, and that the exit code is unaffected (also with `--fail-on`).
  - `sample_output.py`: fill `duplication` and `tool_versions.jscpd` in the fixture JSON where relevant.

## Files to Change
- `python/code_check/js_complexity/reporter.py` — the `Dup` column.
- `python/code_check/js_complexity/executor.py` — the jscpd warning and the docstring/help text.
- `python/tests/code_check/js_complexity/test_reporter.py`, `test_executor.py`, `sample_output.py` — tests and the sample JSON.

## CI Checks
- `python`: `cd python && ruff check . && pytest` (CI jobs: `lint`, `tests`).

## Notes
- Any tests that assert the exact current header or the full table (for example, the selection and config executor tests) need the new column too. Grep the tests for `'Lines'` and `Assessment`.
