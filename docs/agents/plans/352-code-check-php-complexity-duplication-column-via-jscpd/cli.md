# Cli Plan: code_check php_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Documents the report layout and warning defined in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Update the php_complexity long_help
In the `code_check` entry's `long_help` in `commands/python.json` (the "The php_complexity subcommand" part): describe `Dup` next to `Max`, `NPath`, `MI` and `Lines` (the number of the file's lines in exact clones jscpd found among the selected files; information only; `-` when unavailable), mention that a jscpd failure prints a warning and does not change the exit code, and update the example output table to the spec's [duplication.md §4](../../specs/code_check/php_complexity/duplication.md#4-report) example (with the `Dup` column).

## Files to Change
- `commands/python.json` — `php_complexity` section of the `code_check` `long_help`.
