# Spec: `install/installer.sh` update mode

Sub-issue: #265. Parent issue: #263. Shared contracts:
[README.md](README.md), which wins if this file disagrees with it.

## 1. Goal

Add an **update mode** to `install/installer.sh`, so that a newer release's
installer, run from an unpacked release zip in a temp dir, safely updates an
existing web install in place. `tingle update` (#266) downloads and unpacks
the release, then hands off to this mode. The **incoming** release's code
therefore decides how it is laid out on disk, and the code being overwritten
is never the code doing the overwriting.

This sub-issue depends on #264 (hashes in `MANIFEST` and `tingle.json`, and
the `install/manifest.sh` helpers) and must be merged before the 0.4.0 tag.

It covers E1, E3, E5, E11, E12, E13 and E15, the six phases below, and the
safety rules S2 and S3.

## 2. Trigger

This sub-issue **owns** this contract.

| Variable | Meaning |
|----------|---------|
| `TINGLE_UPDATE_TARGET=<install folder>` | Switches on update mode. It skips the target-folder prompt and the "`tingle.json` already exists" refusal. It goes through the same normalization as the prompted target: a leading `~` is expanded and a relative path is made absolute. |
| `TINGLE_UPDATE_FORCE=1` | Overwrites locally edited shipped files (E1). |
| `TINGLE_UPDATE_CLEANUP=1` | Removes the source tree (the dir the installer runs from) when update mode finishes or fails (S3). `tingle update` sets it. Unset, for example when a user runs the installer by hand from a folder they unpacked, the source tree is left alone. |
| `TINGLE_REPO` | Repo recorded in the new `tingle.json`, as today. |
| `TINGLE_VERSION` | Version recorded in the new `tingle.json`, as today. |

- Without `TINGLE_UPDATE_TARGET`, the first-install path behaves exactly as
  before, and keeps ending with `exec "$target/bin/tingle" install`.
- The copy and `tingle.json`-writing code is shared between both paths. The
  first-install path may also switch to the rename-based copy if that keeps
  the code simpler, but it is not required.
- Update mode uses the `install/manifest.sh` helpers from #264 (hashing, the
  two-format `tingle.json` reader, the `MANIFEST`-to-JSON writer). It
  requires `jq`.

In the rest of this file, **target** is `TINGLE_UPDATE_TARGET`, **source** is
the unpacked release tree the installer runs from (the temp dir), the **old
manifest** is the one in `<target>/tingle.json`, and the **new manifest** is
`<source>/MANIFEST`.

## 3. Phases

An interrupted or failed update must leave the install **fully old**, **fully
new**, or in a state that **re-running the update fixes**. It is never stuck.
The approach is: stage everything, swap quickly, and write `tingle.json` last
as the commit point. There is no backup or restore step. Update mode runs
these phases in order.

### 3.1 Preflight (nothing changes yet)

1. **Lock (E15):** take a lock directory in the target,
   `<target>/.tingle-update.lock/`, created with `mkdir` (atomic), holding a
   `pid` file with the installer's PID. If the lock exists and its PID is a
   running process, exit non-zero with a clear message that another update is
   in progress. If that process is gone (or the `pid` file is missing), the
   lock is stale: clear it, say so, and take it.
2. **Writable (E11):** check the target is writable. Otherwise fail early,
   naming the folder.
3. **`tingle.json` validity (E3):** read the old `tingle.json`. If it can't
   be parsed, or `version`, `repo` or `manifest` is missing, exit non-zero and
   change nothing.
4. **Incoming `MANIFEST`:** if `<source>/MANIFEST` is missing, malformed or
   empty, refuse and change nothing, so a broken release tree can never prune
   the whole install.
5. **Edited-file check (E1):** hash every file listed in the old manifest and
   compare it with the recorded hash.
   - A file counts as **unedited** when it matches the old recorded hash
     **or** the incoming release's hash for the same path (from the new
     manifest). The second rule lets a re-run finish an interrupted update
     without the half-applied files looking like local edits.
   - A file listed in the old manifest but missing on disk is not an edit.
     An interrupted prune leaves exactly that state, and the re-run must
     still go through.
   - Any other mismatch: abort, change nothing, and list the edited files,
     unless `TINGLE_UPDATE_FORCE` is set, in which case they are overwritten.
   - When the old manifest has no hashes (the path-only format from before
     0.4.0, `version: "unknown"`, or a hand-built install), edits can't be
     detected: print a warning that local edits to shipped files will be
     overwritten, and continue. This is decided from the **format** of
     `tingle.json` (`tingle_json_tracks_hashes`), not from the version string.

Every exit from preflight releases the lock it took.

### 3.2 Stage

- Write every file listed in the new manifest as a temp file **next to its
  target**, in the same directory: `<dir>/.<name>.tingle-new`. Missing
  directories are created.
- Each staged file keeps the source file's permissions (executable bits), so
  executable scripts stay executable after the swap.
- `MANIFEST` itself (not listed in it) is staged and swapped too, so
  `<target>/MANIFEST` always matches the new `tingle.json`.
- On any failure or signal (a full disk, permissions, Ctrl-C), a trap removes
  the staged files and the lock, and the install is left **untouched**.
- A leftover `.<name>.tingle-new` from an earlier killed run is overwritten.

### 3.3 Swap

- `mv` each staged file over its target. These are renames within the same
  directory, so they are fast and almost never fail.
- `INT` and `TERM` are ignored during this phase (`trap '' INT TERM`).

### 3.4 Prune (E5, E12, E13)

- Delete the **stale** files: those in the old manifest that aren't in the new
  one. Then delete the directories they leave empty. Directories that still
  hold user-added files are kept (E12).
- Files in neither manifest (user-added) are never touched.
- **Empty old manifest (E5):** `[]` deletes nothing, and a warning says stale
  files may be left behind.
- **Unsafe paths (E13):** a manifest path that is absolute or contains `..`
  is skipped with a warning, so a tampered `tingle.json` can't delete files
  outside the install folder. The same rule applies to every path the
  installer hashes (edited-file check), stages, swaps or prunes, in both the
  old and the new manifest.

### 3.5 Commit

- Write the new `tingle.json` (new `version` and `repo` from `TINGLE_VERSION`
  and `TINGLE_REPO`, and the new manifest as `{path, sha256}` entries) to a
  temp file in the target, then rename it over `<target>/tingle.json`.
- Until this step, `tingle.json` still describes the old version.

### 3.6 Wire

- Run `<target>/bin/tingle install` **as a child process, not with `exec`**,
  so the traps still fire (S3).
- Release the lock. Only when `TINGLE_UPDATE_CLEANUP=1`, also remove the temp
  dir the installer runs from (the source). Without it, the source tree is
  left alone.
- The final message names the target, the new version, and says that
  already-open shells need a restart or `source ~/.bashrc` for the new
  completion.

## 4. Safety

- **S2. Replace files by writing a temp file and renaming it, never with `cp`
  in place.** Bash reads a script bit by bit while it runs, and `cp` over an
  existing file rewrites the same file on disk (same inode), so a script still
  being read could run half-old, half-new lines. A rename creates a new file
  on disk, so any other process still holding the old file (for example a
  `tingle` command running in another terminal) keeps reading an intact old
  copy. It also swaps each file all at once.
- **S3. The installer owns cleaning up the temp dir.** `tingle update` ends
  with `exec` (S1, #266) and sets no trap of its own, because `exec` drops
  traps. In update mode, `installer.sh` sets a `trap` that, when
  `TINGLE_UPDATE_CLEANUP=1` (set by `tingle update`), removes the temp dir it
  runs from, whether the update finishes or fails. When the variable is unset
  (the installer run by hand), the source tree is never removed. Deleting a
  running script's folder is safe on Unix. This
  is why it runs `bin/tingle install` as a child process: with `exec`, the
  trap would never fire. The first-install path keeps its current `exec`.

## 5. Recovery

`tingle.json` is written last, so wherever a run is cut off, re-running
`tingle update` either has nothing to do or simply does the update again.

| Cut off during | Resulting state | What re-running does |
|----------------|-----------------|----------------------|
| Preflight | Untouched, fully old. | Runs the update from scratch. |
| Stage (error or signal) | Untouched: the trap removed the staged files. | Runs the update from scratch. |
| Stage (`kill -9`, power loss) | Old install plus leftover `.tingle-new` files and a stale lock. | Clears the stale lock, overwrites the leftovers, and runs the update. |
| Swap | Some files new, some old; `tingle.json` still old; stale lock. | Clears the lock. Swapped files match the incoming hash, so they count as unedited (E1), and the update is redone. |
| Prune | All files new, some stale files left; `tingle.json` still old; stale lock. | Clears the lock and redoes the update, which finishes the prune. |
| Commit | The rename is atomic: `tingle.json` is either the old one (as for prune) or the new one. | With the old one, redoes the update. With the new one, the install is fully new and `tingle update` reports it is up to date. |
| Wire | Fully new install; the `~/.bashrc` block may not be rewired; stale lock; the temp dir may be left. | `tingle update` reports it is up to date and clears the stale lock on its next update. `tingle install` can be re-run by hand to rewire `~/.bashrc`. |

A stale lock left by a killed run is always detected from its PID and cleared
(E15).

## 6. Rejected alternatives

- **Back up the whole install and restore on failure:** more code, double the
  disk use, and the restore itself can fail. It adds little over the staged
  approach.
- **Build a new sibling folder and swap folders:** truly atomic, but the
  user's files would have to be copied, and the folder's identity changes
  under any shell whose working directory is inside it.

## 7. Testing

There is no shell test framework, and none is added. Test standalone, without
the `tingle update` command, against trees built with
`scripts/release_cli.sh build <tag>` and a throwaway `HOME` (so the real
`~/.bashrc` is never touched):

- Install build A with the first-install path. Build a newer B, unpack it,
  and run `TINGLE_UPDATE_TARGET=<folder> <B>/install/installer.sh`. Files are
  added, changed and removed; user-added files are kept; `tingle.json` is
  rewritten; the `~/.bashrc` block is correct.
- An edited shipped file aborts with no changes, and `TINGLE_UPDATE_FORCE=1`
  overwrites it.
- A path-only (pre-0.4.0) `tingle.json` warns and continues. An empty
  manifest warns about stale files.
- A corrupt `tingle.json`, an unwritable folder, and a missing, malformed or
  empty incoming `MANIFEST` leave the install untouched.
- A tampered manifest path (absolute or with `..`) is skipped with a warning.
- Killed during staging: untouched. Killed after staging: re-running finishes
  it.
- `<target>/MANIFEST` matches the new release, and executable files stay
  executable.
- The source tree is removed with `TINGLE_UPDATE_CLEANUP=1` and kept without
  it.
- A relative or `~`-prefixed `TINGLE_UPDATE_TARGET` updates the right folder.
- A second concurrent run is refused, and a stale lock is cleared.
- Without `TINGLE_UPDATE_TARGET`, a first install behaves as before.
- `shellcheck` passes.

## 8. Permanent home

Before #270 deletes this spec, the header comment of `install/installer.sh`
must cover: update mode and its trigger, the env vars
(`TINGLE_UPDATE_TARGET`, `TINGLE_UPDATE_FORCE`, `TINGLE_UPDATE_CLEANUP`,
`TINGLE_REPO`, `TINGLE_VERSION`), the lock, the six phases, S2 and S3, and the recovery
behaviour.
