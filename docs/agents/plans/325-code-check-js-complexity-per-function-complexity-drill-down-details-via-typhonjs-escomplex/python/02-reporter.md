# Reporter function lines
Extend `Reporter.report(parsed, min_level, top, details=None)`:
- With `details` set, print the row's functions under each **shown** level row (after `--min-level`/`--top`), never under PARSE rows. Sort by `(-cyclo, line, name)` and keep the first `details` (all when 0).
- Use the function-line format from the spec, with the row's `display_path(line)` as `path`.
- `functions is None` prints the dim unavailable note, and `[]` prints nothing.

Add a static `select_functions(functions, details)` helper and update the module docstring.

Tests: sorting and ties, `N`/`0`, shown rows only (with `--top`/`--min-level`), no lines under PARSE, the note for `None`, nothing for `[]`, and no output change when `details` is `None`.

## Files to Change
- `python/code_check/js_complexity/reporter.py`: the details rendering.
- `python/tests/code_check/js_complexity/test_reporter.py`: the new tests.
