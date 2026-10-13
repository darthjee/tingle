# Tests

Use the existing `rubycritic` tests as the pattern (`test_flags.py`, `test_selection.py`, `test_executor.py`), with `docker` mocked as the current js_complexity executor tests do, and check the file list sent on the container's stdin.

- `test_flags.py`: the five new flags (names, actions, defaults, help texts, the default list inside the `--exclude` help).
- `test_executor.py` (or a new `test_executor_selection.py` if the file gets too long):
  - `--exclude` adds to the defaults; a second `--exclude` replaces the first; blank entries are dropped.
  - `--no-default-excludes` alone and with `--exclude`; declaration files are still skipped with `--no-default-excludes`.
  - `--ignore` and `--include` are repeatable; `--include` and the extensions both have to match (`--include '**/*.json'` selects nothing).
  - gitignore is on by default inside a git work tree made with `git init` in `tmp_path`; untracked ignored files are skipped and tracked files are kept. `--no-gitignore` keeps the ignored files. Outside a work tree, nothing is skipped and nothing is printed.
  - Filter order: a file matching several steps is dropped by the first. Assert through `FileCollector`'s call or the observable result, as `rubycritic`'s tests do.
  - Single-file `<path>`: the directory excludes don't apply; `--ignore` and `--include` match the file name.
  - Symlinks inside, outside, absolute-inside and dangling; upper-case extensions; declaration files with every suffix and case. Add only what `test_selection.py` doesn't already cover.
- `python/tests/code_check/test_completion.py`: extend `test_js_complexity_flag_names` with the five new flags in order, and add a case showing that `--exclude`, `--ignore` and `--include` take free-form values (same as the `rubycritic` completion tests).

## Files to Change
- `python/tests/code_check/js_complexity/test_flags.py`
- `python/tests/code_check/js_complexity/test_executor.py` (and maybe a new `test_executor_selection.py`)
- `python/tests/code_check/js_complexity/test_selection.py` — only for gaps
- `python/tests/code_check/test_completion.py`
