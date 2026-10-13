# Executor wiring, warning and long help
- Add `"details": None` to `SINGLE_DEFAULTS`. This enables the negative-value check that already lives in `docker_check` and the config merge.
- Pass `options["details"]` to `reporter.report`.
- In `_print_warnings`, after the jscpd one, warn for each `escomplex` warning without a `path`: `escomplex failed in {image}; per-function data is not available: {message}`. Warnings with a `path` aren't printed.
- Update the module docstring (the long help): describe `--details`, add `details` to the config key list, and add example lines `--details` / `--details 0`.

Tests: `--details` alone means 5, with `N`, `0`, and negative (exit 1). Config `details` precedence: built-in < config < CLI. The warning prints for a path-less escomplex entry and not for one with a path, and the exit code is unchanged.

## Files to Change
- `python/code_check/js_complexity/executor.py`: defaults, the report call, the warning and the docstring.
- `python/tests/code_check/js_complexity/test_executor.py`, `test_executor_config.py`: the new tests.
