# Wire, cleanup and header comment
**Wire:** run `"$target/bin/tingle" install` as a child process (not `exec`)
so the traps fire. Then release the lock and, only when
`TINGLE_UPDATE_CLEANUP=1`, remove `$SOURCE_ROOT` (the tree the installer
runs from). Print a final message naming the target and the new version,
saying already-open shells need a restart or `source ~/.bashrc` for the new
completion.

**Header comment:** rewrite the header of `install/installer.sh` so it is the
permanent home of this behaviour once #270 deletes the spec: both modes and
the trigger, every env var (`TINGLE_UPDATE_TARGET`, `TINGLE_UPDATE_FORCE`,
`TINGLE_UPDATE_CLEANUP`, `TINGLE_REPO`, `TINGLE_VERSION`), the lock, the six
phases, the rename rule (S2), who cleans up the temp dir (S3, now gated on
`TINGLE_UPDATE_CLEANUP`), the unsafe-path rule, and the recovery table
(where a run can be cut off and what a re-run does). Update the "already
exists" refusal message to point at `tingle update`.

## Files to Change
- `install/installer.sh` — wire phase, cleanup, header comment, refusal message.
