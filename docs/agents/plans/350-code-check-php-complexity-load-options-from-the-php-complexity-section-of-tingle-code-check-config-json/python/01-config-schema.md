# Real config schema

Replace the stub in `python/code_check/php_complexity/config.py` with the real `SCHEMA`, built from `code_check.validators` exactly like `python/code_check/js_complexity/config.py` but without `details`:

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
}
```

Rewrite the module docstring and the `validate` docstring to match `js_complexity`'s: keys are checked in the section's order, there is no `ext` key (the `.php` set is fixed), the thresholds are not compared with each other, and `details` is unknown until #351.

## Files to Change
- `python/code_check/php_complexity/config.py` — the real `SCHEMA`, imports and docstrings.
