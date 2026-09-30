# Cli Plan: code_check: rename config section check_file_size to file_size (legacy key still read)

Main plan: [plan.md](plan.md)

## Shared contracts

- Section name `file_size`. The legacy `check_file_size` section is still read,
  with a deprecation warning on stderr. Setting both sections is a config
  error (exit 1). See [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Update the `code_check` long_help configuration block
In `commands/python.json`, edit the `"Configuration:"` block of
`code_check.long_help`:
- change `in its "check_file_size" section` to `in its "file_size" section`;
- change the example to `{"file_size": {"warn": 300, "exclude": ["fixtures"], "gitignore": false, "fail_on": "error"}}`,
  and re-align the continuation line under the new, shorter key;
- add a short note: a legacy `"check_file_size"` section is still read, with a
  deprecation warning on stderr; setting both sections is an error (exit 1).

Leave `check_file_size.long_help` unchanged: it has no config example, only a
pointer to `tingle --help code_check`. Keep the JSON valid, and keep the escaped
`\n` line layout within the width of the existing block.

## Files to Change
- `commands/python.json` — the Configuration block in `code_check.long_help`.

## Notes
- Validate with `python3 -m json.tool commands/python.json >/dev/null`, and
  check the output of `bin/tingle --help code_check`, or the repo's equivalent
  help entry point.
