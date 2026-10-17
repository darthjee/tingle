# Tests

Add tests modelled on `python/tests/code_check/js_complexity/test_config.py` and `test_executor_config.py`, covering the list in spec §7:

- `test_config.py`: every key's valid and invalid values with the exact reasons in spec §2. This includes booleans given as numbers, `NaN`/infinity, negative numbers, a float `top`, an empty `image`, a bad `fail_on`/`min_level`, `fail_on: null`, the unknown `ext` and `details` keys, the key-order rule (first bad key reported) and that an empty section is valid.
- `test_executor_config.py`:
  - single values: default < config < CLI, and a config `null` means unset;
  - list merging and deduplication for `exclude`, `ignore` and `include`, with default excludes in front;
  - `no_default_excludes` (config and CLI) dropping the defaults and the `bootstrap/cache` rule but not the Blade skip;
  - `gitignore: false` and `--no-gitignore` winning;
  - `image` from the config avoiding the `VERSION` read;
  - `--no-config` with a broken file;
  - a missing file or missing section (no `Config:` line);
  - an empty section (`Config:` line printed);
  - `php_complexity` not an object, invalid JSON, a top level that is not an object, an unreadable file;
  - errors exiting 1 before any selection or Docker call;
  - a file with only `file_size`/`rubycritic`/`js_complexity` sections loading the defaults.
- `test_flags.py`: `--no-config` is present and parses to `True`.
- `python/tests/code_check/test_completion.py`: add `"--no-config"` to the end of the expected `php_complexity` flag list.
- `python/tests/code_check/php_complexity/test_executor.py`: update the module docstring ("the config file is never read before #350") to say that HOME is an empty temp dir, so no config is loaded.

## Files to Change
- `python/tests/code_check/php_complexity/test_config.py` — new.
- `python/tests/code_check/php_complexity/test_executor_config.py` — new.
- `python/tests/code_check/php_complexity/test_flags.py` — `--no-config`.
- `python/tests/code_check/php_complexity/test_executor.py` — the docstring.
- `python/tests/code_check/test_completion.py` — the expected flag list.
