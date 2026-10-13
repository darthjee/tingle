# Cli Plan: code_check js_complexity: skip minified bundles (*.min.js) by default

Main plan: [plan.md](plan.md)

## Shared contracts

- `--no-default-excludes` help: `Do not skip the default directories or minified bundles; only --exclude names apply`.
- Minified bundles (`.min.js`, `.min.mjs`, `.min.cjs`, any case) are skipped by default, also for a single-file `<path>`; only `--no-default-excludes` / `no_default_excludes` turns this off; `--include` never brings them back.

## Implementation Steps

### Step 1 — Update the js_complexity long_help
In `commands/python.json`, in the `code_check` `long_help`, **only the js_complexity part** (not `file_size` or `rubycritic`):
- reword the `--no-default-excludes` entry to "Do not skip the default directories or minified bundles; only --exclude names apply.", wrapped to the existing column layout;
- in the extensions paragraph after `--include` ("Files with the extensions ... Declaration files ... are always skipped."), add that minified bundles (`.min.js`, `.min.mjs`, `.min.cjs`, any case) are skipped unless `--no-default-excludes` is given, even when `<path>` is a single file or matches `--include`;
- in the single-file sentence ("When <path> is a single file, the directory excludes do not apply ..."), keep it consistent with the above.

No completion change: no new flag.

## Files to Change
- `commands/python.json` — js_complexity `long_help` text.

## Notes
- Keep the JSON valid (`python -m json.tool commands/python.json`) and keep the line width of the surrounding help.
