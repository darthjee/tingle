# Write installer-update-mode.md (#265)
Create `docs/agents/specs/update_command/installer-update-mode.md`, linking
#265. It covers:
- **Trigger:** `TINGLE_UPDATE_TARGET` skips the target prompt and the
  "`tingle.json` already exists" refusal. `TINGLE_UPDATE_FORCE=1` overwrites
  edited files. Without the trigger, first install behaves exactly as before
  (it keeps its `exec`).
- **Phases** (verbatim from #263, Atomicity and Rollback):
  1. Preflight: lock with PID and stale-lock clearing (E15), writable check
     (E11), `tingle.json` validity (E3), and the edited-file check (E1, with
     the old-hash **or** incoming-hash rule, and the warning path when there
     are no hashes).
  2. Stage `.<name>.tingle-new` files next to their targets, with a trap
     that removes them.
  3. Swap by `mv`, with `trap '' INT TERM`.
  4. Prune stale files and the directories they leave empty (E12). Skip
     unsafe paths (E13). An empty manifest deletes nothing and warns (E5).
  5. Commit `tingle.json` via temp file and rename.
  6. Wire: `bin/tingle install` as a **child** process (S3), then release the
     lock and remove the temp dir, with the "restart your shell" message.
- **Safety:** why a rename and not `cp` (S2, inodes), and why the installer
  owns temp-dir cleanup (S3).
- **Recovery:** the table of where a run can be cut off → the resulting state
  → what re-running does.
- **Rejected alternatives:** backup-and-restore, and swapping sibling
  folders.
- **Testing:** the standalone scenarios from #265, run against unpacked
  `release_cli.sh build` trees with a throwaway `HOME`.
- **Permanent home:** the header comment of `install/installer.sh` (update
  mode, env vars, phases, recovery).

## Files to Change
- `docs/agents/specs/update_command/installer-update-mode.md`: new.
