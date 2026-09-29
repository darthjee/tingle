# Up to date, --check and confirmation
**Up to date (E4):** if the installed version is not `unknown` and equals the
target, print exactly `tingle is already up to date (<version>)` and exit 0.
With `--check` this also exits 0 with the same message.

**`--check`:** print `<installed> → <target>` (`unknown → X` for a standalone
install). When `tingle_json_tracks_hashes "$TINGLE_FOLDER/tingle.json"`
succeeds, loop over `tingle_json_entries` (split each line on the first two
spaces). For every path that exists as a regular file under the install and
whose `tingle_sha256` differs from the recorded hash, list it under
`Locally edited shipped files (use --force to overwrite them):`. Skip
unsafe paths (absolute or containing `..`), and skip a missing file. Then exit
0 without downloading anything.

Outside `--check`, print the same `<installed> → <target>` line.

**Confirmation (spec 3.4):** unless `TINGLE_ASSUME_YES` is set, ask
`Proceed? [y/N] ` on `/dev/tty` and read the reply from it. Copy the
`install/bootstrap.sh` logic: no `/dev/tty` means abort with a hint to set
`TINGLE_ASSUME_YES=1`, and anything but `y|Y|yes|YES` prints `Aborted.` and
exits non-zero.

## Files to Change
- `shell/update/executor.sh` — up-to-date check, `--check` report,
  confirmation.
