# Wire the config into the flags and executor

**flags.py**: append the `--no-config` flag (`"action": "store_true"`, help `Do not read ~/.tingle/code_check/config.json`) after `--include`. Update the module docstring to mention it.

**executor.py**: follow `CheckFileSize`:

- Add `CONFIG_SECTION = "rubycritic"` and `LIST_KEYS = ("ignore", "include")`.
- `_load_config(cls, no_config) -> tuple[dict, Path | None]`:
  - With `--no-config`, return `({}, None)` without touching the file.
  - Otherwise call `load_section(CONFIG_SECTION, default_path())`.
  - A missing file or section returns `({}, None)`. A present section returns `(validate(section, path), path)`.
  - `ConfigError` goes to `cls._fail(str(exc))`, which prints `Error: <path>: <reason>` and exits 1.
- `_merge(cls, cli, config) -> dict` replaces `_apply_defaults`:
  - **Single values:** for each `SINGLE_DEFAULTS` key, use the CLI value when it is not None, else `config.get(key, default)`. `details` and `fail_on` are single values; config `null` means "unset", the same as the default.
  - **Lists:** for each of `LIST_KEYS`, `list(dict.fromkeys(config.get(key, []) + (cli[key] or [])))`.
  - **`exclude`:** `config.get("exclude", []) + parse_excludes(cli["exclude"])`, deduplicated.
  - **Booleans:** `no_default_excludes` is `cli or config.get(..., False)`, and `gitignore` is `not cli["no_gitignore"] and config.get("gitignore", True)`.
- Make `_selection_options` read the merged values: `exclude` is now a list (no `parse_excludes`) and `gitignore` is a resolved boolean (not `no_gitignore`).
- `run`:
  1. Parse.
  2. `config, config_file = self._load_config(cli["no_config"])`.
  3. `self._validate(self._merge(cli, config))`.
  4. `_execute(options, config_file)`.

  The config load happens before `_resolve_target`, `resolve_image`, file selection and every Docker call. `resolve_image(options["image"])` is unchanged, and it only reads `VERSION` when the merged `image` is still None.
- `_print_header(out, target, options, image, config=None)` prints `Config: <path>` (dim) after the `Image:` line when `config` is not None.
- Update the module docstring with a configuration paragraph (section, keys, precedence, `--no-config`, exit 1 on invalid config) and a `--no-config` example, the same way `file_size/executor.py` does.

## Files to Change
- `python/code_check/rubycritic/flags.py` — add `--no-config`.
- `python/code_check/rubycritic/executor.py` — `_load_config`, `_merge` (replacing `_apply_defaults`), `_selection_options`, the header `Config:` line, `run` and the docstring.
