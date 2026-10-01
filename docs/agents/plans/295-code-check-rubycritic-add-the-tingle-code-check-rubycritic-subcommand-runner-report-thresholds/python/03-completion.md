# Completion for rubycritic

`python/code_check/completion.py` is currently hard-wired to `file_size`:
- it imports `code_check.file_size.flags.FLAGS` only;
- it builds the module-level `FILE_SIZE_FLAGS` and `FILE_SIZE_VALUE_FLAGS`;
- `_scan()` reads `FILE_SIZE_VALUE_FLAGS` directly;
- `complete()` returns `[]` for any other subcommand.

Refactor it to work per subcommand:
- Add a helper that builds `(flag_names, value_flags)` from a FLAGS list.
- Add a table `{"file_size": ..., "rubycritic": ...}` built from `code_check.file_size.flags.FLAGS` and `code_check.rubycritic.flags.FLAGS`.
- Make `_scan` take `value_flags` as a parameter.
- Dispatch `complete()` through the table.

Expected rubycritic behaviour:
- `--min-level` and `--fail-on` complete their choices.
- `--warn`, `--error`, `--critical`, `--top` and `--image` complete nothing.
- The positional path returns the `__tingle_files__` sentinel.

`file_size` completion must behave exactly as before.

Tests:
- rubycritic flag names, choices, value flags and the path sentinel;
- `file_size` still behaves the same (regression);
- `test_subcommand_names_match_executor_table` still passes;
- extend `test_completion_imports_no_heavy_module` so completion never imports `code_check.rubycritic.executor`, `docker_runner`, `output_parser` or `reporter`.

## Files to Change
- `python/code_check/completion.py`: per-subcommand flag tables, and rubycritic completion.
- `python/tests/code_check/test_completion.py`: rubycritic cases and the extended heavy-module list.
