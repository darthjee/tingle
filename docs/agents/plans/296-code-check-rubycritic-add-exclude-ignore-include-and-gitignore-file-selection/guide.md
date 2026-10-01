# Guide Plan: code_check rubycritic: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

Relies on the five flags and behaviour listed in [plan.md](plan.md#shared-contracts),
implemented by the python agent and mirrored in `long_help` by the cli agent.

## Implementation Steps

### Step 1 — Document file selection in the rubycritic guide

In `docs/guides/code_check/rubycritic.md`:

- **Usage**: directory bullet mentions the selection filters and links to the
  new section; single-file bullet says a symlink is resolved first (its target's
  parent is mounted), excludes do not apply, and globs match the file name.
- **Options table**: add the five flags with defaults; note there is no `--ext`.
- **New "File selection" section**, adapted from `docs/guides/code_check/file_size.md`:
  `--exclude` (16 Ruby defaults, component match, case-insensitive, last
  `--exclude` wins, invocation → excluded names table), `--no-default-excludes`
  (use `--exclude .git`), `.gitignore` / `--no-gitignore` (git rules, tracked
  files kept, silent fallback, host-only since the image has no git),
  `--ignore` / `--include` (glob syntax, quoting, case-insensitive, `--include`
  and `.rb` must both match, `--ignore` wins, excludes always win), filter order,
  and symlinks (directory symlinks not followed, outside/dangling skipped, kept
  symlink shown as target and counted once, absolute-inside works).
- **Skipped files**: summarise all drop reasons and point to the new section;
  keep the default list, no-binary-check bullet, unsendable-name warnings, and
  the "No Ruby files found" bullet (also when filters leave nothing).
- **Examples**: add a few (`--exclude spec,db`, `--ignore 'db/migrate/**'`,
  `--include 'app/**'`, `--no-gitignore`, `--no-default-excludes --exclude .git`).
- **Exit status**: optionally note "(or all filtered out)" on the no-files row.
- **Limitations**: remove the "No file filters yet." bullet.

## Files to Change
- `docs/guides/code_check/rubycritic.md` — sections above.

## Notes
- No markdown lint in the repo or CI; follow the existing guide style by hand
  (no language tag on fences, ~78-char lines).
- `docs/guides/code_check.md` and `docs/guides/README.md` need no change.
