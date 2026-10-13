# Tests

Add tests under `python/tests/code_check/js_complexity/`, following the existing declaration-file tests in `test_selection.py` (selection level) and `test_executor_selection.py` (executor level, through `_run` and the config):

- `is_minified`: `.min.js`, `.min.mjs`, `.min.cjs` in lower, upper and mixed case → True; `.min.ts`, `app.js`, a file named exactly `min.js` → False.
- Directory selection: minified files in any case skipped by default; kept with `skip_minified=False`; `.min.ts` kept; still skipped with `include=["**/*.min.js"]` (selects nothing).
- Executor: skipped by default; kept with `--no-default-excludes`; kept with `"no_default_excludes": true` in the config; still skipped with `--include '**/*.min.js'`.
- Single-file `<path>` that is `bundle.min.js`: nothing analysed, `NO_FILES_MESSAGE`, exit 0, no Docker call; analysed with `--no-default-excludes`.
- Declaration files stay skipped with `--no-default-excludes` (already covered by #321 tests; keep them passing).
- `--no-default-excludes` help text in `test_flags.py` if help is asserted there.

`file_size`'s and `rubycritic`'s tests must pass unchanged.

## Files to Change
- `python/tests/code_check/js_complexity/test_selection.py` — predicate and selection tests.
- `python/tests/code_check/js_complexity/test_executor_selection.py` — flag, config, `--include` and single-file tests.
- `python/tests/code_check/js_complexity/test_flags.py` — help text, if asserted.
