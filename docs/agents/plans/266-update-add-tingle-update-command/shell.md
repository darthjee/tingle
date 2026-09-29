# Shell Plan: update: add tingle update command

Main plan: [plan.md](plan.md)

## Shared contracts

- `shell/update/main.sh run [args...]` `exec`s `executor.sh "$@"`
  (flow-verb layout, like `shell/uninstall/main.sh`). The cli agent points
  `commands/shell.json` `update.path` at `shell/update/main.sh`.
- CLI: `tingle update [--check] [--force] [<version>]`, `TINGLE_VERSION`
  (the argument wins), `TINGLE_ASSUME_YES`.
- Fixed messages, printed exactly:
  `tingle is already up to date (<version>)`,
  `release <version> not found in <repo>`,
  `tingle update can only install 0.4.0 or later`.
- Test-only hooks `TINGLE_RELEASE_API_URL` (default
  `https://api.github.com/repos/<repo>`) and `TINGLE_RELEASE_BASE_URL`
  (default `https://github.com/<repo>/releases/download`), documented only in
  the executor header.
- Handoff environment for the new release's `install/installer.sh` (#265):
  `TINGLE_UPDATE_TARGET=<folder>`, `TINGLE_UPDATE_CLEANUP=1`,
  `TINGLE_REPO=<repo>`, `TINGLE_VERSION=<target>`, plus
  `TINGLE_UPDATE_FORCE=1` with `--force`.
- Helpers from `<tingle root>/install/manifest.sh` (#264): `tingle_sha256`,
  `tingle_json_check`, `tingle_json_entries`, `tingle_json_tracks_hashes`.

## Steps

- [01 — Scaffold shell/update/ and the executor header](shell/01-scaffold.md)
- [02 — Parse arguments and detect the install](shell/02-detect-install.md)
- [03 — Resolve and validate the target version](shell/03-resolve-target.md)
- [04 — Up to date, --check and confirmation](shell/04-check-and-confirm.md)
- [05 — Download, verify and hand off](shell/05-download-and-handoff.md)
- [06 — Manual test pass](shell/06-manual-tests.md)

## Notes
- Follow [update-command.md](../../specs/update_command/update-command.md) section by section.
  Section 3 is the executor's flow, in order.
- **S1:** the executor sets **no** `trap`. Every failure after
  `mktemp -d` removes the temp dir itself before exiting. The `exec` is
  the very last line that runs.
- Stay Bash 3.2 compatible (macOS): no associative arrays, no `mapfile`,
  no `${var,,}`.
- `set -euo pipefail`, like the other executors. Source
  `install/manifest.sh` after it (the library sets no options itself).
- There is no shell test framework, so testing is manual (step 06).
  `shellcheck` must pass on both new files.
