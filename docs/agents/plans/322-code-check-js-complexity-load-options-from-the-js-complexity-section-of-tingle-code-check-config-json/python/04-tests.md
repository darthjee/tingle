# Tests
Add tests under `python/tests/code_check/js_complexity/`, modelled on `python/tests/code_check/rubycritic/test_config.py` and `test_executor_config.py` (HOME is pointed at a temp dir by the autouse fixture in `conftest.py`):

- `test_config.py` — every key's valid values and invalid values with the exact reason from spec §2: booleans as numbers, `NaN`/infinity, negative numbers, floats for `top`, non-list / non-string list items, empty `image`, bad `fail_on`/`min_level`, `fail_on: null` accepted, `ext` and `details` → `unknown key`, first bad key reported in section order, empty section valid.
- `test_executor_config.py` — each single-value precedence rule (default < config < CLI, config `null` = unset), list merging and deduplication for `exclude`/`ignore`/`include` (config first), `no_default_excludes` and `gitignore` interplay with the CLI flags, `--no-config` with a broken file (not read), missing file, missing section, empty section (prints `Config:`), `Config:` header present/absent, invalid JSON / top level not object / section not object / unknown key → `Error: <path>: <reason>` exit 1 with no Docker call, `image` from config avoiding the `VERSION` read, and a file with only `file_size`/`rubycritic` sections loading the defaults.
- `test_flags.py` — `--no-config` parses to `no_config=True` and defaults to `False`.
- Remove or update any existing test that asserted the config file is ignored (e.g. in `test_executor.py`).

## Files to Change
- `python/tests/code_check/js_complexity/test_config.py` — new.
- `python/tests/code_check/js_complexity/test_executor_config.py` — new.
- `python/tests/code_check/js_complexity/test_flags.py` — `--no-config`.
- `python/tests/code_check/js_complexity/test_executor.py` — drop "no config" assumptions if any.
- `python/tests/code_check/test_completion.py` (or equivalent) — expected flag list, if it enumerates js_complexity flags.
