# Cli Plan: update: add tingle update command

Main plan: [plan.md](plan.md)

## Shared contracts

- Add key `"update"` to `commands/shell.json` with
  `"path": "shell/update/main.sh"`. The shell agent provides that script.
- `long_help` documents: usage `tingle update [--check] [--force] [<version>]`,
  the version pin (`X.Y.Z` or `X.Y.Z-<suffix>`, 0.4.0 or later, downgrades
  and pre-releases allowed, argument wins over `TINGLE_VERSION`), `--check`,
  `--force`, `TINGLE_VERSION`, `TINGLE_ASSUME_YES`, and that git checkouts
  are updated with `git pull` instead.
- `long_help` must **not** mention `TINGLE_RELEASE_API_URL` or
  `TINGLE_RELEASE_BASE_URL`.

## Implementation Steps

### Step 1 — Register the `update` command
Add an `update` entry to `commands/shell.json`, between `linux` and
`uninstall` to keep the keys sorted. Match the tone and layout of the
`install` and `uninstall` entries:

- `short_help`: one line, e.g. "Update a web install of tingle to the latest
  or a pinned release."
- `long_help`: what it updates (a web install with `tingle.json`, always the
  folder of the running `tingle`), the usage line, "latest" meaning the
  latest stable GitHub release, the pin rules, `--check`, `--force`,
  `TINGLE_ASSUME_YES`, that files the user added are kept, the git-checkout
  message, and a pointer to `docs/guides/update.md` (added by #267).

### Step 2 — Verify dispatch and help
Check that `jq . commands/shell.json` parses, that `tingle help` lists
`update`, that `tingle help update` prints the `long_help`, and that
bash completion offers `update` (completion reads the command list, so no
change there should be needed; confirm it).

## Files to Change
- `commands/shell.json` — new `update` entry.

## Notes
- Keep `long_help` consistent with the header of
  `shell/update/executor.sh` and the spec's section 2. #267 will write
  `docs/guides/update.md` against it.
