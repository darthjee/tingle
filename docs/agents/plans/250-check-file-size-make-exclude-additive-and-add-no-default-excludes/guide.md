# Guide Plan: check_file_size: make --exclude additive and add --no-default-excludes

Main plan: [plan.md](plan.md)

## Shared contracts

- `--exclude a,b` adds to the defaults; `--no-default-excludes` drops them.
- Matching: whole path component, case-insensitive, relative to `<path>` only; not
  applied to a single-file `<path>`; names are not globs (use `--ignore`).
- The examples table and the migration note in [plan.md](plan.md#shared-contracts) must
  be used as given.

## Implementation Steps

### Step 1 — Rewrite the `--exclude` docs
In `docs/guides/check_file_size.md`:
- Options table: `--exclude LIST` — "Comma-separated directory names to skip, added to
  the defaults."; add a `--no-default-excludes` row (default off).
- `### --exclude` section:
  - Keep the default list.
  - Say that a file is skipped when any part of its path **relative to `<path>`**
    matches a name, case-insensitively and as a whole component (`build` does not
    match `builder`).
  - Remove the "Passing `--exclude` replaces the default list" warning, the "repeat
    the default list" workaround, and the "match covers the whole absolute path"
    caveat (with its `~/work/build/my-app` example). Both behaviours are gone.
  - Add the examples table and the migration note from the shared contracts.
  - Note that names are not globs, and point to `--ignore`.
- Add a `--no-default-excludes` subsection: it drops the defaults, so `.git/` and
  `node_modules/` are walked too; combine with `--exclude` to choose exactly which
  names to skip.
- Check the other `--exclude` mentions (the glob section "still skipped whatever the
  globs say", single-file `<path>`, "Skipped files", "Hidden directories not in the
  exclude list", and the later examples such as
  `--exclude node_modules,dist,build`). Reword them so they no longer imply
  replacement, and change the example to something additive (e.g.
  `--exclude fixtures`).

## Files to Change
- `docs/guides/check_file_size.md` — options table, `--exclude` section, new
  `--no-default-excludes` subsection, related mentions and examples.

## Notes
- Keep in line with `long_help` in `commands/python.json` and the `executor.py`
  docstring (see the guide agent's rules).
