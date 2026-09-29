# Cli Plan: check_file_size: make --exclude additive and add --no-default-excludes

Main plan: [plan.md](plan.md)

## Shared contracts

- Rely on the `python` agent providing `--exclude` (adds to the defaults) and
  `--no-default-excludes` (`store_true`).
- Wording: `--exclude` "adds to the defaults".

## Implementation Steps

### Step 1 — Update `long_help` for `check_file_size`
In `commands/python.json`, `check_file_size.long_help`:
- Under "File selection:", add aligned entries (same column layout as `--ignore` /
  `--include`):
  - `--exclude a,b` — Extra directory names to skip (comma-separated). Adds to the
    defaults (node_modules, dist, build, .git, ...). Whole path components relative to
    <path>, case-insensitive.
  - `--no-default-excludes` — Do not skip the default directories; only --exclude
    names apply.
- In "Examples:", keep a `--exclude` example that now reads as additive (e.g.
  `./check_file_size.py ./src --exclude fixtures`) and add
  `./check_file_size.py . --no-default-excludes --exclude fixtures`.
- Keep the JSON valid (escaped `\n`), and keep the examples consistent with the
  `executor.py` module docstring.

## Files to Change
- `commands/python.json` — `check_file_size.long_help`.

## Notes
- Check if a test asserts on the `long_help` content (e.g. under `python/tests/` or
  `bin/` tests) and update it if needed.
