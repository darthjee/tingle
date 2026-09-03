# cli Plan: Execution: shell subcommand (the anchor command)

Main plan: [plan.md](plan.md)

## Shared contracts

- Document exactly `tingle linux shell` (no flags/args) as the usage
  example, matching what `shell`'s `_handle_shell` implements.

## Implementation Steps

### Step 1 — Add a usage example for `tingle linux shell`

In `commands/shell.json`, extend the `linux` entry's `long_help` with a
concrete usage example/description for the `shell` subcommand (e.g. what it
does — opens an interactive shell in the container with the cwd mounted),
alongside the existing generic usage list.

## Files to Change

- `commands/shell.json` — add a usage example for `tingle linux shell` to
  the `linux` entry's `long_help`.

## Notes

- `sed`'s usage example is out of scope here (tracked in a separate issue,
  #38) — only add detail for `shell`.
