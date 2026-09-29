# Cli Plan: check_file_size: load options from ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

Document the behaviour in [plan.md](plan.md#shared-contracts): config location, keys, precedence, `--no-config`, the `Config:` header line, config errors → exit 1.

## Implementation Steps

### Step 1 — Update long_help
In the `check_file_size` `long_help`:
- add a "Configuration:" block: location `~/.tingle/code_check/config.json`, `check_file_size` section, the key names (flag name with `-` → `_`, `gitignore` is the inverse of `--no-gitignore`), precedence (CLI wins for single values, lists are merged), and `--no-config`;
- add `--no-config` to the options;
- extend the exit code 1 line with "invalid config file";
- add an example `./check_file_size.py . --no-config`.
Keep the existing column alignment.

## Files to Change
- `commands/python.json` — `check_file_size.long_help`.

## Notes
- Check the JSON stays valid (`python3 -m json.tool commands/python.json`).
