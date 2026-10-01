# Cli Plan: code_check rubycritic: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

Relies on the five flags and behaviour listed in [plan.md](plan.md#shared-contracts),
implemented by the python agent in `python/code_check/rubycritic/flags.py`.

## Implementation Steps

### Step 1 — Add a "File selection" block to the rubycritic long_help

In `commands/python.json`, `"code_check"` → `"long_help"`, rubycritic section:
insert a `File selection:` block right after
`<path> is a Ruby file or a directory (analysed recursively).` and before
`Thresholds:`, matching `file_size`'s layout (flags indented 4 spaces,
descriptions at column 36, wrapped lines indented 35, lines <= ~83 chars).
Describe `--exclude a,b`, `--no-default-excludes`, `--no-gitignore`,
`--ignore GLOB`, `--include GLOB` (`Only analyse .rb files ...`, no `--ext`),
followed by a short paragraph on symlinks (outside/missing targets skipped, kept
symlink analysed as its target) and single-file `<path>` (excludes do not
apply, globs match the file name).

### Step 2 — Add examples

After `tingle code_check rubycritic ./app --fail-on error` and before the
`--image` example, add examples such as `--exclude fixtures`,
`--no-default-excludes --exclude fixtures`, `--no-gitignore`,
`--ignore 'spec/**' --ignore '*_spec.rb'`, `--include 'app/**' --include 'lib/**'`.

## Files to Change
- `commands/python.json` — rubycritic part of `code_check`'s `long_help`.

## CI Checks
- repo root: `jq empty commands/python.json` and `bin/tingle code_check --help` (no dedicated CI job; `bin/tingle` validates the JSON at runtime)

## Notes
- Encode newlines as `\n` and quotes as `\"` in the JSON string.
- `--details` (from #291) is missing from `long_help`; out of scope here.
