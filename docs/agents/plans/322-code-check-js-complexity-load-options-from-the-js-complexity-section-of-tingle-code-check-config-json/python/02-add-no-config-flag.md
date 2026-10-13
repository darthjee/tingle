# Add the --no-config flag
Append the `--no-config` `store_true` flag to `FLAGS` with the help text `Do not read ~/.tingle/code_check/config.json` (identical to `rubycritic/flags.py`). Extend the module docstring with a short paragraph like rubycritic's: `--no-config` skips the `js_complexity` section; the file is read and validated by the executor (`js_complexity.config`), which this module never imports — keep `flags.py` cheap to import.

## Files to Change
- `python/code_check/js_complexity/flags.py` — add `--no-config`; docstring.
