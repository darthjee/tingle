# Restructure installer and add the update-mode trigger
Refactor `install/installer.sh` into small functions so the two paths share
code, then branch on `TINGLE_UPDATE_TARGET`.

- Extract target normalization (`~` expansion, relative → absolute) into a
  function and apply it to both the prompted target and
  `TINGLE_UPDATE_TARGET`.
- Extract `tingle.json` writing into a function that writes to a temp file
  in the target and renames it into place (used by both paths; for first
  install the rename is harmless).
- When `TINGLE_UPDATE_TARGET` is set: skip the `/dev/tty` prompt and the
  "`tingle.json` already exists" refusal, require `jq` (fail with a clear
  message if missing), and run the update phases (steps 02–04). Otherwise
  keep today's flow unchanged, including `cp -R` and the final `exec`.
- Add a path-safety helper (rejects absolute paths and any `..` component)
  used by every later phase.

## Files to Change
- `install/installer.sh` — function extraction, update-mode branch, path-safety helper.
