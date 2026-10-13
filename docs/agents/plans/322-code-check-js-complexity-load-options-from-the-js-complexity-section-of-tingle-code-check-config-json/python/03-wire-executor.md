# Wire the config into the executor
In `python/code_check/js_complexity/executor.py`:

- Remove the temporary `_parse` override (the real `--no-config` flag now supplies `no_config`) and the `_load_config` stub, so `DockerCheck._load_config` / `_merge` apply.
- Import `load_section` from `code_check.config` and `validate` from `code_check.js_complexity.config`; set `validate_config = staticmethod(validate)` and add a `_load_section(name, path=None)` staticmethod returning `load_section(name, path)` (same as `rubycritic/executor.py`, so tests can patch the module-level `load_section`).
- Update the `CONFIG_SECTION` comment (drop "read from #322") and the module docstring: replace "There is no config file yet." with the config description (section, keys, precedence, list merge, `--no-default-excludes`/`--no-gitignore` winning, invalid config → `Error: <path>: <reason>` exit 1 before selection/Docker, `--no-config`), add an `Example config:` line, add "invalid config" to the exit-1 list, and add `tingle code_check js_complexity . --no-config` to the examples.
- Make sure `resolve_image(options["image"])` still receives the merged value so a config `image` avoids reading `shell/linux/VERSION` (it already does via `_merge`; just verify).

## Files to Change
- `python/code_check/js_complexity/executor.py` — remove stubs, add `validate_config` / `_load_section`, docstring.
