# Executor and --no-config flag

- In `python/code_check/php_complexity/flags.py`, append the `--no-config` entry (copy `js_complexity/flags.py`'s: `store_true`, help `"Do not read ~/.tingle/code_check/config.json"`) after `--include`, and add a docstring paragraph like `js_complexity`'s saying that `--no-config` skips the `php_complexity` section and that the file is read and validated by the executor, which this module never imports.
- In `python/code_check/php_complexity/executor.py`:
  - Delete the `_parse` override (the base `DockerCheck._parse` now gets `no_config` from the flag) and the `_load_config` override, so the base class reads `CONFIG_SECTION` through `code_check.config.load_section` and validates it with `validate_config`.
  - Update the `CONFIG_SECTION` comment (drop "read from #350").
  - Rewrite the module docstring: replace "There is no config file yet." with a paragraph mirroring `js_complexity/executor.py` (the config file and section, precedence, config errors exit 1 before selection or Docker, `--no-config` skips the file), add "invalid config file" to the exit-1 list, and add the `--no-config` example.
- Confirm that `image` from the config skips the `VERSION` read (`docker_check` image resolution), and that `no_default_excludes: true` from the config reaches `_selection_options` and drops the `bootstrap/cache` skip (it reads the merged `options`).

## Files to Change
- `python/code_check/php_complexity/flags.py` — the `--no-config` flag and docstring.
- `python/code_check/php_complexity/executor.py` — remove the `_parse`/`_load_config` overrides and update the docstrings and comments.
