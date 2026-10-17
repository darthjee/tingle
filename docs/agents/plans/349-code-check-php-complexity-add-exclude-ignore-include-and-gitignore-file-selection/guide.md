# Guide Plan: code_check php_complexity: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

The guide agent can rely on the five flags and the behaviour in the [plan.md](plan.md#shared-contracts) table. The guide must match them and the cli `long_help`.

## Implementation Steps

### Step 1 — Document the selection flags
In `docs/guides/code_check/php_complexity.md`:
- Options section: add rows for the five flags to the options table. Replace the paragraph saying they "are coming in a later release (#349)" with a short pointer to [File selection](#file-selection).
- File selection section: add a subsection per flag, in `js_complexity.md`'s style (`--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore`/`--include` with the glob rules), plus the filter order. Say that `--no-default-excludes` also turns off the `bootstrap/cache` rule, that Blade templates are skipped whatever the flags are, and that `--exclude bootstrap/cache` matches nothing.
- "Tests and generated code": drop "these options are coming in a later release (#349)" and give the working commands (`--exclude tests`, `--ignore 'tests/**'`, `--ignore '**/*Test.php'`).
- Add selection examples wherever the guide lists example commands.

## Files to Change
- `docs/guides/code_check/php_complexity.md` — the selection flags, filter order and examples.

## Notes
- Do not document the config keys (#350).
