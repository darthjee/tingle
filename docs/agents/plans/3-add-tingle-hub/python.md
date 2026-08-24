# python Plan: Add tingle hub

Main plan: [plan.md](plan.md)

## Shared contracts

- Must relocate the script to exactly `python/check_file_size.py`, keeping its shebang (`#!/usr/bin/env python3`), executable bit, and existing CLI contract (positional `path` plus `--warn`/`--error`/`--critical`/`--top`/`--exclude`/`--ext`) unchanged — the `cli` agent's `commands/python.sh` maps `check_file_size` to this exact path and `bin/tingle` execs it directly with no interpreter wrapping.

## Implementation Steps

### Step 1 — Move check_file_size.py into python/

`git mv bin/check_file_size.py python/check_file_size.py`, preserving the executable bit (already `chmod +x`) and the shebang. No behavioral changes to the script's argument parsing or output.

### Step 2 — Register check_file_size in README

Per this agent's existing convention ("New scripts are registered in the table in `README.md`"), add a row to the `Scripts` table:

| Script | Language | Description |
| --- | --- | --- |
| `check_file_size` | Python | Token efficiency triage: lists source files by line count against configurable warn/error/critical thresholds. |

## Files to Change

- `python/check_file_size.py` — moved here from `bin/check_file_size.py` (via `git mv`), unchanged otherwise.
- `bin/check_file_size.py` — removed (result of the `git mv` above).
- `README.md` — add the `check_file_size` row to the Scripts table.
