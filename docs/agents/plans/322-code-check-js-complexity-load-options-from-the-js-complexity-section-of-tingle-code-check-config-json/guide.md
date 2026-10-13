# Guide Plan: code_check js_complexity: load options from the js_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- Section `js_complexity` in `~/.tingle/code_check/config.json`; keys, precedence and errors as in [plan.md](plan.md#shared-contracts) and spec §2–§6.
- `--no-config` — `Do not read ~/.tingle/code_check/config.json`.

## Implementation Steps

### Step 1 — Add a "Configuration file" section to the js_complexity guide
In `docs/guides/code_check/js_complexity.md`, add a `## Configuration file` section (anchor `#configuration-file`, so the index link works), modelled on `docs/guides/code_check/rubycritic.md`: file location, a key table (key, type, flag equivalent), precedence and list merging, `gitignore` vs `--no-gitignore`, `--no-config`, no `ext` key, error messages (`Error: <path>: unknown key 'ext'`), a JSON example (spec §6 without `details`) and the resulting run. Add `--no-config` to the Options list and an example in `## Examples`.

### Step 2 — Update the code_check guide index
In `docs/guides/code_check.md` "Configuration file": drop "(`js_complexity` does not read it yet)", say all three subcommands read the file, add the row `| js_complexity | js_complexity | [Configuration file](code_check/js_complexity.md#configuration-file) |`, and add a `js_complexity` section to the JSON example.

## Files to Change
- `docs/guides/code_check/js_complexity.md` — new "Configuration file" section, `--no-config` option and example.
- `docs/guides/code_check.md` — table row, intro sentence, example.

## Notes
- Do not document `details`; #325 adds it.
