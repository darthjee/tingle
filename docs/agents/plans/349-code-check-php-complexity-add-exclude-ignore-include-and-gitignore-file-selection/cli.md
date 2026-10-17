# Cli Plan: code_check php_complexity: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

The cli agent can rely on the five flags and the behaviour in the [plan.md](plan.md#shared-contracts) table, which python implements. The `long_help` must use the same names and meanings.

## Implementation Steps

### Step 1 — Update the php_complexity long_help
In the `code_check` entry's `long_help`, in the "The php_complexity subcommand" part, rewrite the "File selection:" block. Model it on the `js_complexity` block: one entry per flag (`--exclude a,b`, `--no-default-excludes`, `--no-gitignore`, `--ignore GLOB`, `--include GLOB`), followed by the glob rules. Keep the existing prose on the `.php` extension, Blade templates (always skipped, even with `--include` or `--no-default-excludes`), `bootstrap/cache` (now "unless --no-default-excludes"), symlinks, single-file `<path>` and the "No PHP files found" message. Note that `.gitignore` is honoured by default. Add selection examples to the subcommand's examples, if it has any.

## Files to Change
- `commands/python.json` — the php_complexity `long_help` file-selection block.

## Notes
- Keep the JSON valid (`python3 -m json.tool commands/python.json`), and wrap lines to the column width the other blocks use.
- Do not mention `--no-config` or the config file (#350).
