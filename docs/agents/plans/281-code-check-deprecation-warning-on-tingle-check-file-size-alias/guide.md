# Guide Plan: code_check: deprecation warning on tingle check_file_size alias

Main plan: [plan.md](plan.md)

## Shared contracts

- Warning text to quote: `Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.` (printed on stderr only, so stdout and exit codes are unchanged).
- Removal: "will be removed in a future release". No version is named.

## Implementation Steps

### Step 1 — Migration note in code_check.md
Add a "Migrating from `check_file_size`" section to `docs/guides/code_check.md`. It says:
- `tingle check_file_size` was renamed to `tingle code_check file_size`;
- the old name is still an alias with the same options, output and exit codes, but prints the deprecation warning on stderr;
- the alias will be removed in a future release, so scripts and CI jobs should switch;
- the `check_file_size` config section is unchanged for now (its rename is tracked separately; do not document #282 behaviour here).

### Step 2 — Update check_file_size.md
`docs/guides/check_file_size.md` currently says the old name "behaves the same way". Change it to say the command is deprecated: it still works, but prints the warning on stderr and will be removed in a future release. Link the migration note in `code_check.md` and keep the link to `code_check/file_size.md`.

## Files to Change
- `docs/guides/code_check.md` — add the migration section.
- `docs/guides/check_file_size.md` — describe the deprecation and link the migration note.

## Notes
- `docs/guides/code_check/file_size.md` line 6 ("that name still works") may get a short "(deprecated, prints a warning)" clause and a link to the migration note. A wider sweep of stale mentions belongs to #283.
- Consider whether `docs/guides/README.md`'s entry "Moved to `code_check file_size`" should say "Deprecated". Keep it a one-word change if so.
