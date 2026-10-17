# Print the per-function lines in the reporter
Mirror `js_complexity/reporter.py` (#325) in `php_complexity/reporter.py`.

- `report(parsed, min_level="ok", top=0, details=None)` passes `details` on to `_print_table`.
- `select_functions(functions, details)` is a static method: it sorts by `(-ccn, line, name)` and keeps `functions[:details]`, or all of them when `details` is 0.
- `_print_functions(line, result, details)`: for `functions is None`, print `f"{c.DIM}{'':<16} (per-function data unavailable){c.RESET}"`. For `[]`, print nothing. Otherwise, for each selected unit, print
  `f"{c.DIM}{'':<16} ccn {f['ccn']:>3}  npath {f['npath']:>7}  {f['name']}  ({path}:{f['line']}){c.RESET}"`, where `path = self.display_path(line)`.
- `_print_table` calls `_print_functions` after each **level** row when `details is not None`, and never for `PARSE` rows. Shown rows are already filtered by `--min-level`/`--top`.
- Update the module docstring (the dim lines, the unavailable note, and that they are information only).
- Tests in `test_reporter.py`: sorting and ties (`ccn`, then `line`, then `name`); `N`, `0` and the default; lines only under shown rows (with `--top` and `--min-level`); never under `PARSE`; the unavailable note for `None` and nothing for `[]`; a large `npath` (> 7 digits, > 2^53) printed in full; the spec §4 example (`Square::__construct` before the other ccn-1 units). Extend `sample_output.py` with `functions` data where it helps.

## Files to Change
- `python/code_check/php_complexity/reporter.py` — `details` parameter, `select_functions`, `_print_functions`, table wiring, docstring.
- `python/tests/code_check/php_complexity/test_reporter.py` — reporter tests.
- `python/tests/code_check/php_complexity/sample_output.py` — sample `functions` data (if needed).
