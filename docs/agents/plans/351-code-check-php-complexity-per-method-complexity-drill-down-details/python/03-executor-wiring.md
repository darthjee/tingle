# Wire the executor and update the long help
- `executor.py`: add `"details": None` to `SINGLE_DEFAULTS`, which also turns on the shared negative check in `DockerCheck._validate`. Pass `options["details"]` to `reporter.report(...)`.
- Update the module docstring, which is the long help. Describe `--details [N]` (alone means 5, `0` = all, never under PARSE, `(per-function data unavailable)` with an older image), add `details` to the config key list and drop the "`details` is unknown until #351" phrase. Add the examples `tingle code_check php_complexity ./src --details` and `... --details 0`.
- Tests:
  - `test_executor.py`: `--details` reaches the reporter; a negative value gives `Error: --details must be an integer >= 0`, exit 1; the exit code is unchanged by unit lines; output with `functions: null` from an older image shows the note.
  - `test_executor_config.py`: config `details` is used, CLI wins over config, and the built-in default is `None`.
  - `python/tests/code_check/test_completion.py`: `--details` is a free-form value flag for `php_complexity`.

## Files to Change
- `python/code_check/php_complexity/executor.py` — `SINGLE_DEFAULTS`, the `report` call, docstring and long help.
- `python/tests/code_check/php_complexity/test_executor.py` — CLI-level tests.
- `python/tests/code_check/php_complexity/test_executor_config.py` — config precedence tests.
- `python/tests/code_check/test_completion.py` — completion test.
