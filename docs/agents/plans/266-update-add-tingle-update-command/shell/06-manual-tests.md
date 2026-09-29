# Manual test pass
There is no shell test framework, and none is added. Build two zips with
`scripts/release_cli.sh build 0.4.0` and `... build 0.4.1` (checksum them
with `sha256sum`/`shasum -a 256` into `tingle-<v>.zip.sha256` if the build
doesn't write one). Lay them out as `<dir>/<v>/tingle-<v>.zip`, and serve
them with `file://` or `python3 -m http.server`, with
`TINGLE_RELEASE_BASE_URL` pointing there. For "latest", point
`TINGLE_RELEASE_API_URL` at a folder with a `releases/latest` JSON file.
Install 0.4.0 into a throwaway `HOME` with `install/installer.sh`, then check
each case:

- An end-to-end update from 0.4.0 to 0.4.1 (`TINGLE_ASSUME_YES=1`). The new
  `tingle.json` and files are in place, and no temp dir is left behind.
- Already up to date, `--check` (clean, and with an edited shipped file), a
  pin, and a downgrade from 0.4.1 to 0.4.0.
- `tingle update 0.3.0` and `tingle update v1` are refused before any
  download.
- Refused with no TTY (`setsid`, or `< /dev/null` without a controlling
  terminal) and no `TINGLE_ASSUME_YES`.
- A 404, a bad `.sha256`, no network (an unreachable URL), a corrupt
  `tingle.json` and an unwritable folder all leave the install unchanged.
- An edited shipped file aborts in the installer, and `--force` goes through.
- A git checkout (this repo) gets the `git pull` message, and a folder with
  neither `tingle.json` nor `.git` is refused.
- `shellcheck shell/update/main.sh shell/update/executor.sh` passes.

## Files to Change
- None (verification only).
