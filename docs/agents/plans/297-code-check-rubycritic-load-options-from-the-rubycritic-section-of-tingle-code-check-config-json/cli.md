# Cli Plan: code_check rubycritic: load options from the rubycritic section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

The `python` agent adds `--no-config` and the `rubycritic` config section; see [plan.md](plan.md#shared-contracts) for the keys, defaults and precedence. This agent documents them in `long_help`.

## Implementation Steps

### Step 1 — Document the config file in long_help
In the `code_check` entry of `commands/python.json`, inside the rubycritic part of `long_help`, add a `Configuration:` block before `Exit codes:`, modelled on the file_size one:

- Defaults can be set in `~/.tingle/code_check/config.json`, in its `"rubycritic"` section (other top-level keys are ignored). Include a short example such as `{"rubycritic": {"warn": 50, "exclude": ["db"], "fail_on": "error"}}`.
- Keys are the flag names with `-` replaced by `_`: warn, error, critical, top, exclude, ignore, include, no_default_excludes, fail_on, min_level, image, details. List keys (exclude, ignore, include) take JSON lists. `"gitignore"` (default true) is the inverse of `--no-gitignore`. There is no `ext`.
- Command-line values win for single values. Lists from the config and the command line are merged. `--no-default-excludes` and `--no-gitignore` always win when given.
- Add a `--no-config` line: `Do not read ~/.tingle/code_check/config.json`.

Also:

- Add `invalid config file` to the exit code 1 description.
- Add `tingle code_check rubycritic . --no-config` to the examples.
- Keep the column alignment used in the rest of the text, and keep the JSON valid.

## Files to Change
- `commands/python.json` — rubycritic `long_help`: Configuration block, `--no-config`, exit code 1 text and an example.

## Notes
- The rubycritic `long_help` does not document `--details` (#291) yet. Adding it is out of scope, but it is a one-line fix if the agent wants to fold it in; mention it in the PR either way.
