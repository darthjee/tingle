# Manual verification
There is no shell test framework and none is added. Using a throwaway `HOME`
and trees from `scripts/release_cli.sh build <tag>` (build A, then a
modified B that adds, changes and removes files), check:

- A → B update: files added/changed/removed, user-added files and dirs kept,
  `tingle.json` and `<target>/MANIFEST` match B, executables still
  executable, `~/.bashrc` block correct.
- Edited shipped file aborts with no changes; `TINGLE_UPDATE_FORCE=1`
  overwrites it.
- Path-only (pre-0.4.0) `tingle.json` warns and continues; `[]` warns about
  stale files.
- Corrupt `tingle.json`, unwritable target, and a missing/empty incoming
  `MANIFEST` leave the install untouched.
- Tampered manifest path (absolute or `..`) is skipped with a warning.
- Kill during staging: untouched. Kill after staging (e.g. `kill -9` during
  swap): re-running finishes the update.
- Concurrent second run refused; stale lock (dead PID) cleared.
- Source tree removed with `TINGLE_UPDATE_CLEANUP=1`, kept without it.
- `TINGLE_UPDATE_TARGET=~/x` and a relative path are normalized.
- First install without `TINGLE_UPDATE_TARGET` behaves as before.
- `shellcheck install/*.sh` passes.

Report the results in the PR description.

## Files to Change
- none (verification only).
