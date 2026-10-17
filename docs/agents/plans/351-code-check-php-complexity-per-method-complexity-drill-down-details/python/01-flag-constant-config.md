# Add the flag, constant and config key
Add the user-facing knobs for `--details`, mirroring `js_complexity`.

- `constants.py`: add `DEFAULT_DETAILS: ClassVar[int] = 5` with the comment `# --details given without N: show this many functions per file` (wording adapted to "functions and methods").
- `flags.py`: add the `--details` entry after `--fail-on`/`--min-level`, as in `js_complexity/flags.py`. Use `type=int`, `nargs="?"`, `const=Constants.DEFAULT_DETAILS` and `default=None`. The help text is `Show the N most complex functions and methods under each file (default when given without N: 5; 0 = all)`, built from the constant.
- `config.py`: add `"details": nullable_non_negative_int` to `SCHEMA`, and import the validator. Update the module and `validate` docstrings, which still say `details` is an unknown key until #351.
- Tests: `test_flags.py` (alone → 5, `N`, `0`, absent → `None`); `test_config.py` (valid int, `0`, `null`, negative and non-int rejected with `'details' must be an integer >= 0 or null`, no longer an unknown key).

## Files to Change
- `python/code_check/php_complexity/constants.py` — `DEFAULT_DETAILS`.
- `python/code_check/php_complexity/flags.py` — `--details` flag.
- `python/code_check/php_complexity/config.py` — `details` in `SCHEMA`; docstrings.
- `python/tests/code_check/php_complexity/test_flags.py` — flag tests.
- `python/tests/code_check/php_complexity/test_config.py` — config key tests.
