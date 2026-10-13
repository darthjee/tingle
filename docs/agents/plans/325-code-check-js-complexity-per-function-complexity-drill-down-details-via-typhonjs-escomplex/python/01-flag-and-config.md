# Flag, constant and config key
- Add `DEFAULT_DETAILS: ClassVar[int] = 5` to `Constants`.
- Add the `--details` flag after `--fail-on`, copying rubycritic's definition but with "functions" in the help text.
- Add `"details": nullable_non_negative_int` to `SCHEMA` and drop the "no `details` key yet" text from the docstrings.
- Update the tests that currently assert `--details` is rejected (`test_flags.py` parametrize `["--details", "--ext"]`, and `test_executor.py` around line 72). Add `details` to the js_complexity flag list in `test_completion.py` and add config tests (valid int, `null`, negative, non-int).

## Files to Change
- `python/code_check/js_complexity/constants.py`: add `DEFAULT_DETAILS`.
- `python/code_check/js_complexity/flags.py`: add `--details`.
- `python/code_check/js_complexity/config.py`: add the `details` key and update the docstrings.
- `python/tests/code_check/js_complexity/test_flags.py`, `test_config.py`, `python/tests/code_check/test_completion.py`: update and add tests.
