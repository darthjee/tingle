# Executor and registration
Implement `executor.py`: `CheckPhpComplexity(DockerCheck)` with the class attributes from cli.md §1 (`PROG`, `FLAGS`, `CONFIG_SECTION = "php_complexity"`, `SINGLE_DEFAULTS` without `details`, `LIST_KEYS`, `THRESHOLD_KEYS`, `DEFAULT_EXCLUDES`, `NO_FILES_MESSAGE`, `error_class`) and the hooks `validate_config`, `select_files`, `_gate_value` (total CCN) and `_execute`. The run order follows §3. `--fail-on` exits 2 and ignores `PARSE` files.

Register the subcommand: add `SUBCOMMAND_NAMES` in `python/code_check/subcommands.py` and `SUBCOMMANDS["php_complexity"]` after `js_complexity` in `python/code_check/executor.py`. In `python/code_check/completion.py`, give `php_complexity` the same completion as `js_complexity`, built from `code_check.php_complexity.flags.FLAGS`.

Add `test_executor.py` with `docker` mocked (no args → help and exit 0, usage errors → exit 1, bad path, empty selection with no Docker call, success, gate → exit 2, `PARSE` never gating). Extend `python/tests/code_check/test_executor.py` and `test_completion.py` for the new subcommand.

## Files to Change
- `python/code_check/php_complexity/executor.py` — new
- `python/code_check/subcommands.py` — add `php_complexity`
- `python/code_check/executor.py` — register `CheckPhpComplexity`
- `python/code_check/completion.py` — `php_complexity` completion
- `python/tests/code_check/php_complexity/test_executor.py` — new
- `python/tests/code_check/test_executor.py`, `python/tests/code_check/test_completion.py` — extend
