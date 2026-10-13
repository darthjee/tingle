# Add the js_complexity config schema
Create `python/code_check/js_complexity/config.py`, mirroring `python/code_check/rubycritic/config.py`: a module docstring describing the `js_complexity` section (no `ext` key — the extension set is fixed; no `details` key until #325; thresholds are not compared with each other; `ConfigError` re-exported from `code_check.config`), `SCHEMA` mapping each key to its `code_check.validators` validator (spec §2, without `details`), and `validate(section, path)` delegating to `validate_section(section, SCHEMA, path)`. `__all__ = ["SCHEMA", "ConfigError", "validate"]`.

## Files to Change
- `python/code_check/js_complexity/config.py` — new; `SCHEMA` and `validate`.
