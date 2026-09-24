# Update long_help
Update the `check_file_size.long_help` string in `commands/python.json`:
mention `--fail-on warn|error|critical`, the exit codes (0 success, 1 error,
2 gate failed) and the colour/`NO_COLOR` behaviour, and add the CI example
`./check_file_size.py ./src --fail-on error` to the Examples list. Mirror the
new example in the module docstring of `python/check_file_size/executor.py`.
Keep the JSON valid.

## Files to Change
- `commands/python.json`: `long_help` for `check_file_size`
- `python/check_file_size/executor.py`: module docstring examples
