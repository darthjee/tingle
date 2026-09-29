# Stage, swap, prune and commit
**Stage:** for every safe path in the new `MANIFEST`, plus `MANIFEST`
itself, `mkdir -p` its directory in the target and copy the source file to
`<dir>/.<name>.tingle-new` with `cp -p` (keeps the executable bits),
overwriting any leftover. Record each staged path in a list file. Set a trap
for `ERR`/`INT`/`TERM`/`EXIT` that removes every staged file, the lock, and
(with `TINGLE_UPDATE_CLEANUP=1`) the source tree, leaving the install
untouched.

**Swap:** `trap '' INT TERM`, then `mv -f` each staged file over its target.
Afterwards restore normal signal handling (the trap no longer removes staged
files, since there are none).

**Prune:** if the old manifest is empty (`[]`), warn that stale files may be
left behind and skip. Otherwise, for each old path not in the new
`MANIFEST` (skipping unsafe paths with a warning), `rm -f` it, then remove
its now-empty parent directories up to (not including) the target with
`rmdir` (which fails harmlessly on non-empty dirs). Never touch files in
neither manifest.

**Commit:** write the new `tingle.json` (`version` = `TINGLE_VERSION`,
`repo` = `TINGLE_REPO`, `manifest` = `tingle_manifest_to_json` of the new
`MANIFEST`) via the temp-file-and-rename helper from step 01.

## Files to Change
- `install/installer.sh` — stage, swap, prune and commit functions.
