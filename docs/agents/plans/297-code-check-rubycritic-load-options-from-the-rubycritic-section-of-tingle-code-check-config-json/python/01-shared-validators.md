# Move the shared validators

Move the generic validators out of `file_size/config.py` into a new module, `python/code_check/validators.py`, so `rubycritic/config.py` can reuse them without importing another subcommand's private names (the spec allows this, as long as `file_size`'s messages and behaviour stay the same).

- Move `Validator` and the four validators to `code_check/validators.py` with public names: `non_negative_int`, `list_of_str`, `boolean` and `one_of(choices, nullable=False)`. Keep the bodies and messages unchanged.
- Add the validators `rubycritic` needs there too, since they are generic:
  - `non_negative_number(key, value)`: accepts an `int` or `float` (not `bool`) that is finite (`math.isfinite`) and ≥ 0. Otherwise it returns `'<key>' must be a number >= 0`.
  - `non_empty_str(key, value)`: accepts a `str` with `value.strip() != ""`. Otherwise it returns `'<key>' must be a non-empty string`.
  - `nullable_non_negative_int(key, value)`: accepts `None` or what `non_negative_int` accepts. Otherwise it returns `'<key>' must be an integer >= 0 or null`.
- The module uses the standard library only.
- In `file_size/config.py`, import the validators from `code_check.validators` and build `SCHEMA` from them. Keep `SCHEMA`, `validate`, `ConfigError` and `__all__`. The generic per-key loop can stay in each `config.py` (it is 8 lines), or become a shared `validate_section(section, schema, path)` helper in `validators.py` that both `validate` functions call. Prefer the shared helper.

## Files to Change
- `python/code_check/validators.py` — new; the shared validators and, optionally, `validate_section`.
- `python/code_check/file_size/config.py` — import the validators instead of defining them.
