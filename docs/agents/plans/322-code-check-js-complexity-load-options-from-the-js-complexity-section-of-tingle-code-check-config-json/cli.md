# Cli Plan: code_check js_complexity: load options from the js_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- Section `js_complexity`; keys `warn, error, critical, top, exclude, ignore, include, no_default_excludes, fail_on, min_level, image`; `gitignore` (default true) is the inverse of `--no-gitignore`; there is no `ext` key (and no `details` yet).
- `--no-config` — `Do not read ~/.tingle/code_check/config.json`.
- Example: `{"js_complexity": {"warn": 40, "exclude": ["generated"], "fail_on": "error"}}`.

## Implementation Steps

### Step 1 — Document the config in the js_complexity long_help
In the `code_check` entry of `commands/python.json`, inside "The js_complexity subcommand:" block, add a `Configuration:` section between `Image:` and `Exit codes:`, worded like the rubycritic one (section name `"js_complexity"`, the key list above without `details`, "There is no \"ext\" key.", precedence sentence, and the `--no-config` line). Add "invalid config file" to the exit-1 list and `tingle code_check js_complexity . --no-config` to the examples. Keep the JSON valid (`python -m json.tool commands/python.json`).

## Files to Change
- `commands/python.json` — js_complexity `Configuration:` section, exit code text, example.

## Notes
- Any test that snapshots `long_help` must be kept in sync (check `python/tests` / `bin` tests for references to this text).
