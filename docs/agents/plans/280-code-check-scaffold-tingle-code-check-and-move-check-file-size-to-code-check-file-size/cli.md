# Cli Plan: code_check: scaffold tingle code_check and move check_file_size to code_check file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- You rely on the python agent to provide `python/code_check/main.py` (100755), which handles `run` and `complete`,
  and `python/code_check/completion.py` beside it. With those in place, the existing `completions/bash/commands.sh`
  picks up completion automatically.
- The `code_check` subcommands are `file_size` only. Its flags, exit codes (0/1/2) and config file
  (`~/.tingle/code_check/config.json`, section `check_file_size`) are unchanged from today's `check_file_size`.
- The `check_file_size` entry stays as it is and still points at `python/check_file_size/main.py`.

## Implementation Steps

### Step 1 — Register code_check in commands/python.json
Add a `code_check` key to `commands/python.json`:
- `path`: `"python/code_check/main.py"`
- `short_help`: a one-liner such as `"Code evaluation checks (subcommands: file_size)."`
- `long_help`: usage lines `tingle code_check <subcommand> [options]` and `tingle code_check <subcommand> --help`, a
  subcommand list with `file_size` and its one-line description, and a `file_size` section covering the same
  content as today's `check_file_size` long_help (file selection, display, CI gate `--fail-on`, configuration,
  exit codes 0/1/2). Write every example as `tingle code_check file_size ...`, replacing the stale
  `./check_file_size.py` wording.

Leave the `check_file_size` entry unchanged; there is no deprecation note in this issue. No changes are needed in
`bin/tingle` or `completions/`, because new JSON keys are picked up automatically.

### Step 2 — Verify dispatch, help and completion
Once the python work is in place, check the following:
- `bin/tingle` lists `code_check`.
- `bin/tingle --help code_check` prints the new `long_help`.
- `bin/tingle code_check` lists `file_size`.
- `bin/tingle code_check file_size .` and `bin/tingle check_file_size .` give identical output and exit code.
- With `completions/tingle.bash` sourced:
  - `tingle code_check <TAB>` → `file_size`
  - `tingle code_check file_size <TAB>` → paths
  - `tingle code_check file_size --<TAB>` → flags
  - `--fail-on <TAB>` → `warn error critical`
  - `tingle check_file_size <TAB>` → paths only

Also check that `commands/python.json` is still valid JSON (`jq . commands/python.json`).

## Files to Change
- `commands/python.json` — add the `code_check` entry.

## Notes
- There are no automated tests for `bin/` or completions; verification is manual.
- The command list pads names to 13 characters (`bin/tingle:78`). `code_check` fits.
