# Cli Plan: check_file_size: add --ignore and --include glob flags

Main plan: [plan.md](plan.md)

## Shared contracts

- Flags `--ignore GLOB` / `--include GLOB`, both repeatable. Globs match the
  path relative to `<path>` (or the file name for a single file), ignore case,
  and follow `.gitignore`-style anchoring. `--ignore` wins over `--include`,
  and `--include` combined with `--ext` is an AND.
- Use the canonical examples from [plan.md](plan.md).

## Implementation Steps

### Step 1 — Update `long_help` for `check_file_size`
In `commands/python.json`, add a short "File selection" block to
`check_file_size.long_help`, next to the existing "CI gate" block. It
describes `--ignore GLOB` and `--include GLOB` (both repeatable, relative
path, `**` crosses directories, `--ignore` wins, AND with `--ext`). Also add
two examples:
`./check_file_size.py . --ignore '*.test.js' --ignore 'docs/**'` and
`./check_file_size.py . --include 'src/**' --ext .py`.
Keep the file valid JSON (escaped `\n`, and the existing style and
alignment).

## Files to Change
- `commands/python.json` — the `check_file_size.long_help` text.

## Notes
- No `bin/` changes are needed. Flags are parsed by the python script.
- Check that `python -m json.tool commands/python.json` still succeeds.
