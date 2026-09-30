# Guide Plan: code_check: rename config section check_file_size to file_size (legacy key still read)

Main plan: [plan.md](plan.md)

## Shared contracts

- Section name `file_size`. Legacy section `check_file_size` is still read.
- Warning (stderr), word for word:
  `Warning: <config path>: 'check_file_size' section is deprecated; rename it to 'file_size'.`
- Error when both are set (stderr, exit 1), word for word:
  `Error: <config path>: both 'file_size' and 'check_file_size' sections are set; keep only 'file_size'`
- `Config:` header line appears when either section was loaded; `--no-config`
  skips the file entirely (no warning, no error).

## Implementation Steps

### Step 1 — `docs/guides/code_check/file_size.md`
In the "Configuration file" section and the places that refer to it, change
the key to `file_size`:
- line ~359 (`the check_file_size key:`), the JSON example at ~363, and the
  "no `check_file_size` key" sentence at ~374;
- line ~425: the `Config:` header note. It shows when a `file_size`
  section, or a legacy `check_file_size` section, was loaded;
- line ~455: the Config errors list. It names `file_size` (or the legacy
  section) when the section is not an object. Also add the "both sections
  are set" reason with its exact message;
- line ~514: the Header description of `Config:`.
Add a short "Legacy `check_file_size` section" subsection under
"Configuration file". It says the old key still works but prints the warning
(show it), that setting both is an error (show it), and how to migrate: rename
the key. Mention that `--no-config` skips both.

### Step 2 — `docs/guides/code_check.md`
- Sections table (~line 66): `file_size` → section `file_size`.
- JSON example (~line 72): use the `"file_size"` key.
- "Migrating from `check_file_size`" (~lines 112–113): replace the "unchanged
  for now" note. Explain that the config section was renamed to `file_size`,
  that the old section is still read with the deprecation warning, and that
  having both is an error. Link to the new subsection in `code_check/file_size.md`.

## Files to Change
- `docs/guides/code_check/file_size.md` — section name, the legacy-key subsection, the errors list, and the header notes.
- `docs/guides/code_check.md` — the sections table, the example, and the migration note.

## Notes
- The line numbers are approximate (as of `main` at d17bccb). Use `grep -n check_file_size`
  on both files to find every mention. Mentions of the *command alias*
  `tingle check_file_size` stay as they are.
