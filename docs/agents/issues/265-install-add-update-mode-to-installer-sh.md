# Issue: install: add update mode to installer.sh

## Description
Add an **update mode** to `install/installer.sh`, so that a newer release's
installer, run from an unpacked release zip, can safely update an existing
web install in place. The `tingle update` command (#266, a later sub-issue of
#263) downloads and unpacks the release, then hands off to this mode. That
way the **incoming** release's code decides how it is laid out on disk.

Sub-issue 2 of 4 of #263. It depends on sub-issue 1 (#264, merged: per-file
hashes in `MANIFEST` / `tingle.json` and the `install/manifest.sh` helpers).
**It must be merged before the 0.4.0 tag.**

The full spec is
[`docs/agents/specs/update_command/installer-update-mode.md`](../specs/update_command/installer-update-mode.md);
the shared contracts in
[`docs/agents/specs/update_command/README.md`](../specs/update_command/README.md)
win if anything disagrees.

## Problem
`install/installer.sh` refuses to run when `<target>/tingle.json` already
exists ("Use the (future) update flow"), and it copies files with
`cp -R`, which is unsafe over a live install.

## Expected Behavior
### Trigger (shared contract, owned here)
- `TINGLE_UPDATE_TARGET=<install folder>` switches on update mode. It skips
  the target-folder prompt and the "`tingle.json` already exists" refusal.
- `TINGLE_UPDATE_TARGET` goes through the same normalization as the
  prompted target (leading `~` expanded, relative paths made absolute).
- `TINGLE_UPDATE_CLEANUP=1` makes update mode remove the source tree (the
  temp dir the installer runs from) when it finishes or fails. `tingle update`
  (#266) sets it; without it, e.g. when a user runs the installer by hand
  from a folder they unpacked, the source tree is left alone.
- `TINGLE_UPDATE_FORCE=1` overwrites locally edited shipped files (see
  edited files below).
- `TINGLE_REPO` / `TINGLE_VERSION` are the new repo and version recorded in
  `tingle.json`, as today.
- Update mode requires `jq` (for the `tingle.json` readers).
- Without `TINGLE_UPDATE_TARGET`, the first-install path behaves exactly as
  before.

### Phases (in order)
An interrupted or failed update must leave the install **fully old**, **fully
new**, or in a state that **re-running the update fixes**, never stuck.

1. **Preflight** (nothing changes yet):
   - Take a lock: `mkdir <target>/.tingle-update.lock/` (atomic) holding a
     `pid` file. If another running update holds it, exit non-zero with a
     clear message. A lock whose process is gone (or with no `pid` file) is
     stale: clear it, say so, and take it. Every exit from preflight
     releases the lock.
   - Check the install folder is writable, and fail early naming it.
   - Read the old `tingle.json`. If it can't be parsed, or `version`,
     `repo` or `manifest` is missing, exit non-zero and change nothing.
   - Refuse (change nothing) if the incoming `MANIFEST` is missing,
     malformed or empty, so a broken release tree can never prune the whole
     install.
   - **Edited-file check:** hash every file in the old manifest. A file
     counts as **unedited** if it matches the old recorded hash **or** the
     incoming release's hash (from the new `MANIFEST`). The second rule lets
     a re-run finish an interrupted update. A file missing on disk is not an
     edit (an interrupted prune leaves that state). Any other mismatch:
     abort, change nothing, and list the edited files, unless
     `TINGLE_UPDATE_FORCE` is set.
   - If the old manifest has no hashes (path-only format from before 0.4.0,
     a `"unknown"` version, or a hand-built install), edits can't be
     detected: print a warning that local edits to shipped files will be
     overwritten, and continue. This is decided from the `tingle.json`
     **format** (`tingle_json_tracks_hashes`), not the version string.
2. **Stage:** write every file in the new manifest as a temp file **next to
   its target** (`.<name>.tingle-new`, same directory), creating missing
   directories and keeping the source file's permissions (executable bits).
   `MANIFEST` itself (not listed in it) is staged too, so
   `<target>/MANIFEST` always matches the new `tingle.json`.
   A leftover `.tingle-new` from an earlier killed run is overwritten. On any
   failure or signal (a full disk, permissions, Ctrl-C), a trap removes the
   staged files and the lock, and the install is left **untouched**.
3. **Swap:** `mv` each staged file over its target. Never `cp` in place:
   bash reads scripts bit by bit, and a rename gives a new inode, so any
   process still reading the old file keeps an intact copy. `INT`/`TERM` are
   ignored during this short phase (`trap '' INT TERM`).
4. **Prune:** delete the files in the old manifest that aren't in the new
   one, then any directories they leave empty. Directories that still hold
   user-added files are kept. Files in neither manifest (user-added) are
   never touched. An empty old manifest (`[]`) deletes nothing and warns that
   stale files may be left behind.
5. **Commit:** write the new `tingle.json` (temp file in the target, then
   rename). Until this step, `tingle.json` still describes the old version,
   so re-running after a crash in phases 3–5 simply redoes the update.
6. **Wire:** run `<target>/bin/tingle install` **as a child process, not with
   `exec`** so the traps still fire, then release the lock and, only when
   `TINGLE_UPDATE_CLEANUP=1`, remove the temp dir the installer runs from
   (safe on Unix even while running). The
   final message names the target and the new version, and says
   already-open shells need a restart or `source ~/.bashrc` for the new
   completion.

### Unsafe paths
Any manifest path that is absolute or contains `..` is skipped with a
warning, for every path the installer writes, checks or deletes, so a
tampered `tingle.json` can't touch files outside the install folder.

## Solution
- `install/installer.sh`: add the update-mode branch and the phases above.
  Share the copy and `tingle.json`-writing code with the first-install path
  (which keeps its current `exec "$target/bin/tingle" install`).
- Reuse `install/manifest.sh` from #264: `tingle_sha256`,
  `tingle_manifest_to_json`, `tingle_json_check`, `tingle_json_entries`,
  `tingle_json_tracks_hashes`.
- The first-install path can also switch to the rename-based copy if that
  keeps the code simpler, but it is not required.
- Update the header comment of `install/installer.sh` to be the permanent
  home of this behaviour (the spec is deleted by #270): update mode and its
  trigger, the env vars, the lock, the six phases, safety rules S2/S3, and
  the recovery behaviour.
- Update the specs in `docs/agents/specs/update_command/` to match this
  issue: `installer-update-mode.md` (the `TINGLE_UPDATE_CLEANUP` flag,
  `TINGLE_UPDATE_TARGET` normalization, replacing `<target>/MANIFEST`,
  refusing a missing/malformed/empty incoming `MANIFEST`, keeping file
  permissions, the unsafe-path rule for every path), plus `README.md` and
  `update-command.md` so that `tingle update` sets `TINGLE_UPDATE_CLEANUP=1`.

## Testing
No shell test framework is added. Test standalone, without the
`tingle update` command, using a throwaway `HOME`:
- Install build A with the first-install path, build a newer B with
  `scripts/release_cli.sh build`, unpack it, and run
  `TINGLE_UPDATE_TARGET=<folder> <B>/install/installer.sh`. Check that files
  were added, changed and removed, user-added files kept, `tingle.json`
  rewritten, and the `~/.bashrc` block correct.
- An edited shipped file aborts with no changes, and `TINGLE_UPDATE_FORCE=1`
  overwrites it. A path-only (pre-0.4.0) `tingle.json` warns and continues.
  An empty old manifest warns about stale files.
- A corrupt `tingle.json`, an unwritable folder and a missing/empty incoming
  `MANIFEST` leave the install untouched.
- A tampered manifest path (absolute or with `..`) is skipped with a warning.
- Kill during staging: untouched. Kill after staging: re-running finishes it.
- `<target>/MANIFEST` matches the new release, and executable files stay
  executable.
- The source tree is removed with `TINGLE_UPDATE_CLEANUP=1` and kept
  without it.
- A second concurrent run is refused, and a stale lock is cleared.
- Without `TINGLE_UPDATE_TARGET`, a first install behaves as before.
- `shellcheck` passes.

## Responsible agent
architect (`install/` has no dedicated specialist).
