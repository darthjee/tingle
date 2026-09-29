# Preflight: lock, checks and edited-file detection
Nothing on disk changes except the lock.

1. **Lock:** `mkdir "$target/.tingle-update.lock"`; on success write `$$` to
   `pid`. If `mkdir` fails, read `pid`; if it names a running process
   (`kill -0`), exit non-zero ("another update is in progress"). Otherwise
   (dead PID or no `pid` file) say the lock is stale, remove it, and retry
   once. Install an `EXIT` trap that releases the lock on every preflight exit.
2. **Writable:** fail early, naming the target, if it isn't a writable
   directory.
3. **`tingle.json`:** `tingle_json_check "$target/tingle.json"` or exit
   non-zero with no change.
4. **Incoming `MANIFEST`:** refuse if `$SOURCE_ROOT/MANIFEST` is missing,
   fails `tingle_manifest_to_json`, or has no entries.
5. **Edited files:** if `tingle_json_tracks_hashes` fails, warn that local
   edits to shipped files will be overwritten and continue. Otherwise, for
   each `tingle_json_entries` line (skipping unsafe paths with a warning):
   missing on disk → fine; hash (`tingle_sha256`) equals the old hash or the
   new `MANIFEST` hash for that path → fine; else record as edited. If any
   are edited and `TINGLE_UPDATE_FORCE` is not `1`, list them and exit
   non-zero; with the flag, warn and continue.

## Files to Change
- `install/installer.sh` — preflight functions and lock handling.
