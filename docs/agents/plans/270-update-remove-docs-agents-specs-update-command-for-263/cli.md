# Cli Plan: update: remove docs/agents/specs/update_command/ for #263

Main plan: [plan.md](plan.md)

## Shared contracts

- `version: "unknown"` is always out of date. `--check` shows
  `unknown → X`.
- The git-checkout path is the #268 one.

## Implementation Steps

### Step 1 — Fill the gaps in the update long_help in commands/shell.json
- Quote the fixed message `release <version> not found in <repo>`, as the
  other two fixed messages are quoted (update-command.md:40).
- Mention that `unknown` is always out of date and that `--check` shows
  `unknown → X` (update-command.md:136).
- Mention that an unknown install (no `tingle.json` and no `.git`) is
  refused (update-command.md:110).

## Files to Change
- `commands/shell.json`: the `update` entry's `long_help` only.

## CI Checks
- `jq . commands/shell.json` must still parse. Also run `pytest` (CI job
  `tests`), in case any test reads `commands/*.json`.
