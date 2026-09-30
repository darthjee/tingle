# Cli Plan: code_check: deprecation warning on tingle check_file_size alias

Main plan: [plan.md](plan.md)

## Shared contracts

- `short_help` must start with exactly `Deprecated: use code_check file_size.`
- `tingle --help check_file_size` is answered by `bin/tingle` from the JSON and never reaches the shim, so the long help itself has to carry the deprecation notice.

## Implementation Steps

### Step 1 — Mark check_file_size as deprecated in commands/python.json
For the `check_file_size` entry (keep `path` unchanged):
- `short_help`: `Deprecated: use code_check file_size.`
- `long_help`: replace the whole duplicated body, which still has stale `./check_file_size.py` examples, with a short pointer of 2–3 lines. For example: "Deprecated: this command has moved to `tingle code_check file_size` and will be removed in a future release. It still works, but prints a warning on stderr.\n\nSee: tingle --help code_check"

Check that `bin/tingle help` lists it within the existing `%-13s` column layout, and that `bin/tingle --help check_file_size` prints the pointer. No `bin/tingle` changes are needed.

## Files to Change
- `commands/python.json` — deprecate the `check_file_size` `short_help` and `long_help`.

## Notes
- The file must stay valid JSON (`jq empty commands/python.json`).
