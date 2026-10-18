# Python Plan: code_check php_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Relies on (produced by shell; the parser already validates the shape):

- `files[i].duplication`: `{"lines": int >= 0}` or `null`, exposed as `FileResult.duplication`.
- A jscpd failure is a `{"tool": "jscpd", "message": ...}` warning without `path`, in `ParsedOutput.warnings`.

Produces:

- Header `f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  {'Dup':>5}  File"`, separator `─` × 16, 5, 5, 7, 5, 5, 5, 50; level row `{n:>5}` or `-`; `PARSE` row `-`.
- stderr `Warning: jscpd failed in <image>; duplication data is not available: <message>` per path-less `jscpd` warning; exit code unchanged.

## Implementation Steps

### Step 1 — Dup column in the reporter
In `python/code_check/php_complexity/reporter.py`, add a `_dup(result)` helper mirroring `code_check.js_complexity.reporter` (`-` when `result.duplication is None`, else `str(result.duplication["lines"])`), insert the `Dup` column between `Lines` and `File` in the header, separator, level rows and `PARSE` rows. The summary, the gate and the `--details` function lines are unchanged (function lines keep their current indentation). Update the module docstring: `Dup` is information only, `-` when there is no duplication data and on `PARSE` rows.

### Step 2 — jscpd warning in the executor, and tests
In `python/code_check/php_complexity/executor.py::_print_warnings`, after the PDepend messages, warn once per `jscpd` warning without a `path` with `jscpd failed in {image}; duplication data is not available: {message}` (pass the image through, as `js_complexity`'s executor does). Update the module docstring (`Dup` described, jscpd failure non-fatal). Tests:
- `test_reporter.py`: header/separator with `Dup`; a row with a number, with `0`, with `null` (`-`); `PARSE` rows show `-`; `--details` output still has the column on file rows.
- `test_executor.py`: the jscpd warning printed for a path-less `jscpd` warning; exit code unchanged (0, and 2 with a failing gate); no warning when there is none.
- `sample_output.py`: give the sample files realistic `duplication` values and `tool_versions.jscpd: "5.4.1"` (matching the spec's fixture: `13` for `dup_a.php`/`dup_b.php`, `0` elsewhere, `null` for parse errors/refused lines); adjust any test that asserted the old table.

## Files to Change
- `python/code_check/php_complexity/reporter.py` — `Dup` column, docstring.
- `python/code_check/php_complexity/executor.py` — jscpd warning, docstring.
- `python/tests/code_check/php_complexity/sample_output.py` — duplication values and jscpd version.
- `python/tests/code_check/php_complexity/test_reporter.py` — column tests.
- `python/tests/code_check/php_complexity/test_executor.py` — warning and exit-code tests.

## CI Checks
- `python/`: `ruff check . && pytest` (CI jobs running `ruff check .` and `pytest` in `.circleci/config.yml`).

## Notes
- `output_parser.py` already validates `duplication` and allows the `jscpd` warning tool and a string `tool_versions.jscpd`; no change expected there beyond docstrings mentioning "later sub-issues".
