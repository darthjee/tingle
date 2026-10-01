# Tests

Add tests and update the existing ones. Use a temporary `HOME` (the `default_path()` value is computed at call time), as `tests/code_check/file_size/test_executor_config.py` does.

- **New `tests/code_check/test_validators.py`:** each shared validator, including `non_negative_number` with `True`, `NaN`, `Infinity`, `-1`, `0`, `1.5`; `non_empty_str` with `""`, `"  "`, `1`; and `nullable_non_negative_int` with `None`, `0`, `-1`, `1.0`, `True`.
- **New `tests/code_check/rubycritic/test_config.py`:** every key's valid and invalid values with the exact reason strings, `ext` as an unknown key, an empty section, and first-bad-key ordering.
- **New `tests/code_check/rubycritic/test_executor_config.py`:**
  - Each single-value precedence rule (default < config < CLI), including `image` and `details`.
  - List merging and deduplication for `exclude`, `ignore` and `include`.
  - `no_default_excludes` and `gitignore` from the config, and the CLI turn-off flags winning.
  - `--no-config` with a broken file (no error).
  - A missing file, a missing section and an empty section (`Config:` line shown or not).
  - Invalid JSON, a non-object top level, a non-object section and an unknown key: exit 1 with `Error: <path>: <reason>` and no Docker call.
  - A config `image` avoiding the `VERSION` read (point `Constants.VERSION_FILE` at a missing file).
- **Existing tests:**
  - `tests/code_check/rubycritic/test_flags.py`: the new flag.
  - `tests/code_check/rubycritic/test_executor.py`: adapt to `_merge` replacing `_apply_defaults`, and keep `HOME` isolated so a real user config can't leak in.
  - `tests/code_check/test_completion.py`: add `--no-config` to `test_rubycritic_flag_names`, and `code_check.rubycritic.config` and `code_check.validators` to the heavy-module list.
  - `tests/code_check/file_size/test_config.py` must pass unchanged.

## Files to Change
- `python/tests/code_check/test_validators.py` — new.
- `python/tests/code_check/rubycritic/test_config.py` — new.
- `python/tests/code_check/rubycritic/test_executor_config.py` — new.
- `python/tests/code_check/rubycritic/test_executor.py` — adapt to the merge and isolate `HOME`.
- `python/tests/code_check/rubycritic/test_flags.py` — `--no-config`.
- `python/tests/code_check/test_completion.py` — flag list and heavy-module list.
