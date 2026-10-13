# Wire no_default_excludes into the selection

`docker_check.executor.Executor._selection_options` (a classmethod) turns the merged options into `select_files` keyword arguments; `no_default_excludes` is already merged there from the flag and the config (CLI `--no-default-excludes` always wins when given).

In `python/code_check/js_complexity/executor.py`, override `_selection_options` to extend the base result with `skip_minified=not bool(options.get("no_default_excludes"))`. `_select_files` already forwards `**kwargs` to `js_complexity.selection.select_files`, so nothing else changes. Do not touch `docker_check/executor.py` (rubycritic's `select_files` has no such argument).

Update the executor module docstring where it describes `--no-default-excludes` (around lines 11–24) to say it also drops the minified skip.

## Files to Change
- `python/code_check/js_complexity/executor.py` — `_selection_options` override; docstring.
