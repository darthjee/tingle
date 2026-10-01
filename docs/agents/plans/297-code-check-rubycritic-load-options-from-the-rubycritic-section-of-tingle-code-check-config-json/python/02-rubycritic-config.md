# Add rubycritic/config.py

Create `python/code_check/rubycritic/config.py`, with the same shape as `file_size/config.py`: a module docstring, `__all__ = ["SCHEMA", "ConfigError", "validate"]`, `ConfigError` re-exported from `code_check.config`, and:

```python
SCHEMA: dict[str, Validator] = {
    "warn": non_negative_number,
    "error": non_negative_number,
    "critical": non_negative_number,
    "top": non_negative_int,
    "exclude": list_of_str,
    "ignore": list_of_str,
    "include": list_of_str,
    "no_default_excludes": boolean,
    "gitignore": boolean,
    "fail_on": one_of(["warn", "error", "critical"], nullable=True),
    "min_level": one_of(["ok", "warn", "error", "critical"]),
    "image": non_empty_str,
    "details": nullable_non_negative_int,
}
```

`validate(section, path)` returns the section unchanged, or raises `ConfigError(path, reason)` for the first bad key, in the section's key order. An unknown key (`ext` included) gives `unknown key '<key>'`. The thresholds are not compared with each other.

## Files to Change
- `python/code_check/rubycritic/config.py` — new; `SCHEMA` and `validate`.
