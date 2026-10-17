# Tests
Cover every case in `selection.md` §9. Model them on `python/tests/code_check/js_complexity/test_executor_selection.py`, which drives the executor end to end through an echo Docker double.

- A new `python/tests/code_check/php_complexity/test_executor_selection.py`:
  - each flag; `--exclude` adds to the defaults; blank `--exclude` entries are dropped; a second `--exclude` replaces the first;
  - `--no-default-excludes`, alone and with `--exclude`, brings back `vendor/`, `storage/` and `bootstrap/cache/` files, but not Blade templates;
  - `--ignore` and `--include` are repeatable; `--include` and `.php` must both match; `--include '**/*.blade.php'` selects nothing; Blade names in any case (`View.BLADE.PHP`);
  - the `bootstrap/cache` rule, positive (`bootstrap/cache/services.php`, `app/Bootstrap/Cache/x.php`) and negative (`bootstrap/app.php`, `cache/bootstrap/x.php`, `bootstrap/other/cache/x.php`); `<path>` inside a cache directory; a single file under `bootstrap/cache/`;
  - `.gitignore` on by default, `--no-gitignore`, a single file, outside a work tree, git missing;
  - the filter order (a file matching several steps is dropped by the first); a single-file `<path>` (directory excludes do not apply, globs match the file name); symlinks inside, outside, absolute-inside and dangling; upper-case extensions.
- `test_flags.py`: the new flags, their defaults, actions and help texts (including that `--exclude` help lists all 16 defaults).
- `test_executor.py`: update any assertion that relied on the placeholder (`gitignore=False`, fixed excludes).
- `python/tests/code_check/test_completion.py`: add the five flags to `PHP_COMPLEXITY_EXPECTED_FLAGS`, and add `--exclude`, `--ignore`, `--include` to the free-value parametrisation.

## Files to Change
- `python/tests/code_check/php_complexity/test_executor_selection.py` — new.
- `python/tests/code_check/php_complexity/test_flags.py` — new flags.
- `python/tests/code_check/php_complexity/test_executor.py` — placeholder assumptions.
- `python/tests/code_check/test_completion.py` — php_complexity expected flags.
