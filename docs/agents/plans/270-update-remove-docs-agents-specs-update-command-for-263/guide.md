# Guide Plan: update: remove docs/agents/specs/update_command/ for #263

Main plan: [plan.md](plan.md)

## Shared contracts

- Code wins over the specs. The git-checkout path is the #268 one
  (`git pull --ff-only` + `tingle install`).
- `version: "unknown"` is always out of date. `--check` shows
  `unknown → X`.
- `"manifest": []` means nothing is deleted, and a warning is printed.
- "Already up to date" on a web install exits 0.

## Implementation Steps

### Step 1 — Fill the behaviour gaps in docs/guides/update.md
- **Interrupting it:** correct the promise that a re-run always finishes an
  interrupted update. If the run is cut off during the final
  `tingle install`, the files are already new, so a re-run says "already
  up to date" and does not rewire `~/.bashrc`. The user must run
  `<folder>/bin/tingle install` by hand (installer-update-mode.md:162-173).
- **Update to the latest release / `--check`:** installed version
  `unknown` is always out of date, and `--check` shows `unknown → X`
  (README.md:194-195, update-command.md:136-137).
- **What it changes and what it keeps:** with an empty manifest, nothing is
  deleted and a warning is printed (installer-update-mode.md:115-116).
  Absolute or `..` paths in `tingle.json` or `MANIFEST` are skipped with
  `skipping unsafe manifest path '<path>'` (installer-update-mode.md:117-121).
- **What it does / Prerequisites:** 0.3.x installs have no `tingle update`.
  `bootstrap.sh` refuses an existing `tingle.json`, so the move to 0.4.0
  is done by hand (README.md:82-84).
- State that "already up to date" on a web install exits 0 (README.md:210).

### Step 2 — Fill the Troubleshooting gaps
Add entries, quoting the real messages from `shell/update/executor.sh` and
`install/update.sh`, for:
- a missing checksum file: `could not download the checksum <url>.sha256
  (HTTP <status>); nothing was changed`;
- a bad zip: `<zip> could not be unzipped`, and `<zip> has no executable
  install/installer.sh`;
- a broken release `MANIFEST` (missing, malformed or empty): refused, with
  nothing changed;
- a missing tool: `required tool '<x>' not found on PATH` (`curl`,
  `unzip`, `jq`);
- `unexpected response (HTTP N)`, and the unreadable `tag_name` error;
- `unknown option` and `unexpected argument`;
- failures in the middle of an update: `could not replace ... re-run the
  update` and `could not write .../tingle.json; re-run`.

## Files to Change
- `docs/guides/update.md`: the sections above.

## Notes
- Copy the message text from the code, not from the specs.
- Keep the guide user-facing. Leave out the test-only hooks
  (`TINGLE_RELEASE_*`) and the internal env vars (`TINGLE_UPDATE_*`).
