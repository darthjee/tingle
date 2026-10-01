# Add the `--details` flag
- `flags.py`: add `{"name": "--details", "type": int, "nargs": "?", "const": 5, "default": None, "help": ...}` using the shared help text from plan.md.
- `executor.py`:
  - Leave `details` out of `SINGLE_DEFAULTS` (or set it to `None`): absent means off.
  - `_validate` rejects a negative value with `--details must be an integer >= 0`.
  - After `_parse_output`, if `options["details"] is not None and parsed.methods is None`, raise `RubycriticError` with the missing-key message from plan.md.
  - Pass `options["details"]` to `reporter.report`.
  - Add `--details` to the module docstring examples.
- Tests in `test_flags.py` and `test_executor.py`: `--details` alone → 5, `--details 3`, `--details 0`, negative → exit 1, missing key with and without `--details`.

## Files to Change
- `python/code_check/rubycritic/flags.py`: new flag.
- `python/code_check/rubycritic/executor.py`: validation, missing-key error, pass-through.
- `python/tests/code_check/rubycritic/test_flags.py`, `test_executor.py`: tests.
