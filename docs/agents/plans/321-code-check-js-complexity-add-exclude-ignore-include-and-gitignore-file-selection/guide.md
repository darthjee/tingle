# Guide Plan: code_check js_complexity: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

The five flags, the filter order, gitignore on by default, and the single-file rules, all as in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Rewrite "Which files are analysed" as "File selection"
In `docs/guides/code_check/js_complexity.md`, use `docs/guides/code_check/rubycritic.md`'s "File selection" section (`--exclude`, `--no-default-excludes`, ".gitignore and `--no-gitignore`", "`--ignore` and `--include`", "Filter order", "Single-file targets", "Symlinks") as the template, adapted to JS/TS:
- Rename the section heading to "File selection"; keep the anchors other sections link to working, or update those links.
- Keep "Extensions" (with declaration files always skipped, even with `--no-default-excludes`), "Default excludes" (19 names), "Symlinks", "Unusual file names" and "Nothing to analyse".
- Remove "There is no `.gitignore` filtering" and describe the gitignore default instead.
- Filter order list: default excludes, `--exclude`, gitignore, `--ignore`, `--include` and the extensions, declaration files, symlink confinement.
- Single-file targets: the directory excludes don't apply and the globs match the file name.
- Examples: `--exclude test,fixtures`, `--ignore '**/*.test.ts'` / `'**/*.spec.js'`, `--include 'src/**'`, `--no-gitignore`.

### Step 2 — Update the rest of the guide
- "Options": list the five new flags, or point to "File selection".
- "Examples": add a couple of selection examples.
- "Limitations": drop any "no selection flags" or "no .gitignore" line, and keep "no config file yet".
- "Quick help": paste the new `--help` output from the cli agent's `long_help` change.

## Files to Change
- `docs/guides/code_check/js_complexity.md`

## Notes
- Don't document the minified skip (#323) or the config keys (#322) yet.
