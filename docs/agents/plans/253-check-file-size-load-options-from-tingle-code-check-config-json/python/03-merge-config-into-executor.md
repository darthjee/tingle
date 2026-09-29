# Merge config into executor

In `python/check_file_size/executor.py`:

1. **FLAGS**: `--warn`, `--error`, `--critical`, `--top` default to `None` (help text keeps showing the built-in default). `--min-level` and `--fail-on` already default to `None`. Add `--no-config` (`store_true`, help: "Do not read ~/.tingle/code_check/config.json").
2. **Load**: after `_parse` and before `_resolve_target`, unless `args["no_config"]`: `section = load_section("check_file_size")`; if not `None`, `validate(section, path)`. Catch `ConfigError`, print `Error: <path>: <reason>` in red with `Palette(sys.stderr)` and `sys.exit(1)` (same style as "path not found"; consider a shared `_fail(msg)` helper).
3. **Merge**: one classmethod `_merge(cli: dict, config: dict) -> dict` returning the resolved args:
   - single values (`warn`, `error`, `critical`, `top`, `fail_on`, `min_level`): CLI if not `None`, else config if the key is present (note `fail_on: null` is a present `None`), else built-in default (`Constants.DEFAULT_*`, `top=0`, `min_level="ok"`, `fail_on=None`);
   - `exclude`: config list + `_parse_excludes(cli["exclude"])`, deduplicated — feed it into `_resolve_excludes` (adjust it to take the merged list);
   - `ignore`, `include`, `ext`: config list + CLI list, deduplicated (`dict.fromkeys`);
   - `no_default_excludes`: `cli flag or config.get("no_default_excludes", False)`;
   - `gitignore`: `False` if `--no-gitignore`, else `config.get("gitignore", True)`.
   Replace the ad-hoc `args["min_level"] or "ok"` / `or []` handling in `run` with the merged dict.
4. **Header**: `_print_header` takes the loaded config path (or `None`) and prints `f"{out.DIM}Config: {path}{out.RESET}"` after the `Thresholds:` line when a section was loaded.
5. **Docstring**: mention the config file in the module docstring and add a `--no-config` example.

Keep `run` under the complexity limit (Codacy flagged CC 12 before): push the load/merge work into helpers.

## Files to Change
- `python/check_file_size/executor.py` — `None` defaults, `--no-config`, load/validate/merge helpers, header line, docstring.
