# Cli Plan: code_check js_complexity: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

The five flags and their behaviour as in [plan.md](plan.md#shared-contracts). Completion is generated from `FLAGS` by `code_check.completion` (the python agent's work), so this side has no completion code to change.

## Implementation Steps

### Step 1 — Update `long_help` for js_complexity
In `commands/python.json`, in the `js_complexity` part of `code_check`'s `long_help`, rewrite "File selection:" to match `rubycritic`'s block:
- `--exclude a,b`, with the defaults abbreviated as "node_modules, dist, build, ..., .turbo, .svelte-kit, .output, .vercel, .parcel-cache, storybook-static".
- `--no-default-excludes`, which ends at "directories; only --exclude names apply." (#323 extends it).
- `--no-gitignore`, with the same text as `rubycritic`.
- `--ignore GLOB` ("Wins over --include").
- `--include GLOB` ("Only analyse JavaScript/TypeScript files ...").
- The glob note.

Keep the paragraphs on extensions and declaration files, and on symlinks and single files. Add "and the globs match the file name" to the single-file sentence.

Add these lines to the "Examples:" list:
- `tingle code_check js_complexity ./src --exclude fixtures`
- `tingle code_check js_complexity . --no-default-excludes --exclude fixtures`
- `tingle code_check js_complexity . --no-gitignore`
- `tingle code_check js_complexity . --ignore '**/*.test.ts' --ignore 'docs/**'`
- `tingle code_check js_complexity . --include 'src/**'`

Leave `file_size` and `rubycritic` alone.

### Step 2 — Check the help and completion
Run `bin/tingle code_check js_complexity --help` and `bin/tingle code_check --help` to check the layout and the column alignment. Then check that tab completion after `js_complexity src ` offers the new flags.

## Files to Change
- `commands/python.json` — the `js_complexity` "File selection" block and examples in `long_help`.

## Notes
- If a test asserts on `long_help` (search `python/tests` and `bin` tests for "js_complexity"), coordinate with the python agent so the test moves with the text.
