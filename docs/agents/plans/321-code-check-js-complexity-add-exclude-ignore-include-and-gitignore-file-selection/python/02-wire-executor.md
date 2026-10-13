# Wire the flags in the executor

In `CheckJsComplexity`:
- Set `LIST_KEYS = ("ignore", "include")`, as in `rubycritic`, so `DockerCheck._merge` dedupes the repeated globs.
- Delete the `_selection_options` override (the comment says #321 removes it). The base `DockerCheck._selection_options` then resolves `exclude` with `resolve_excludes(DEFAULT_EXCLUDES, ...)` and passes `ignore`, `include` and `gitignore`. `gitignore` defaults to `True` through `_merge`, which computes `not no_gitignore and config.get("gitignore", True)`, and `_load_config` still returns `{}`.

Update the module docstring:
- The "File selection" paragraph: drop "There are no selection flags, no `.gitignore` filtering"; describe the flags and the filter order as `rubycritic`'s docstring does; keep "no config file yet".
- Usage examples: add `--exclude test,fixtures`, `--no-default-excludes --exclude vendor`, `--ignore '**/*.test.ts'`, `--include 'src/**'` and `--no-gitignore`.

Check that `js_complexity/selection.py`'s `gitignore=False` default and its docstring ("off by default until the selection flags land") still read right. The executor always passes `gitignore` explicitly, so change only the docstring wording and keep the signature as it is.

## Files to Change
- `python/code_check/js_complexity/executor.py` — set `LIST_KEYS`, delete `_selection_options`, update the docstring.
- `python/code_check/js_complexity/selection.py` — docstring wording only.
