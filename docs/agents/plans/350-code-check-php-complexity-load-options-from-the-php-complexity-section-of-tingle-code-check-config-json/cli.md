# Cli Plan: code_check php_complexity: load options from the php_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- New flag `--no-config` ("Do not read ~/.tingle/code_check/config.json").
- Config section `php_complexity` with keys `warn, error, critical, top, exclude, ignore, include, no_default_excludes, fail_on, min_level, image` plus `gitignore` (default true, the inverse of `--no-gitignore`). There is no `ext` key, and `details` is not a key yet.

## Implementation Steps

### Step 1 — php_complexity long_help
In `commands/python.json`, the `code_check` `long_help`, in the php_complexity part:
- Add a `Configuration:` block after `Image:`, copied from the js_complexity one with the `php_complexity` section name and an example such as `{"php_complexity": {"warn": 25, "exclude": ["generated"], "fail_on": "error"}}`. List the same keys (no `details`), the "gitignore (default true)" sentence, "There is no \"ext\" key.", the merge rules and the `--no-config` line.
- Add "invalid config file" to the exit-1 description.
- Add the example `tingle code_check php_complexity . --no-config`.
- Keep the JSON valid (`python3 -m json.tool commands/python.json`).

## Files to Change
- `commands/python.json` — the php_complexity section of the `code_check` `long_help`.

## Notes
- Line wrapping and indentation must match the neighbouring js_complexity block.
