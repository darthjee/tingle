# Architect Plan: release: add per-file SHA-256 hashes to MANIFEST and tingle.json

Main plan: [plan.md](plan.md)

## Shared contracts

This agent **produces** every contract in [plan.md](plan.md#shared-contracts):
the `MANIFEST` line format, the `tingle.json` schema, the
`install/manifest.sh` function interface, and `install` in `INCLUDES`. They
must match [`manifest-hashes.md`](../../specs/update_command/manifest-hashes.md)
section 3 exactly, because #265 and #266 build on them.

## Steps

- [01 — Add the install/manifest.sh library](architect/01-add-manifest-library.md)
- [02 — Hash files in MANIFEST and ship install/](architect/02-release-cli-manifest-hashes.md)
- [03 — Write {path, sha256} entries in tingle.json](architect/03-installer-tingle-json.md)

## CI Checks
CircleCI only runs `scripts/release_cli.sh build`/`publish` on tags; no CI
job lints shell. Run locally:
- `shellcheck install/manifest.sh install/installer.sh scripts/release_cli.sh`
- `scripts/release_cli.sh build 0.0.0-test`, then check `unzip -p dist/tingle-0.0.0-test.zip MANIFEST`
  and that the zip lists `install/installer.sh` and `install/manifest.sh`
  (remove `dist/tingle-0.0.0-test.zip*` afterwards).

## Notes
- There is no shell test framework and none is added. Verify by hand, as in
  the issue's Testing section: the build, the unpacked installer against a
  throwaway `HOME` (pipe `</dev/null` or let the prompt fall back to the
  default; set `HOME` to a temp dir so `~/.bashrc` is not touched), the reader
  on an old and a new `tingle.json` plus a corrupt one, and both hash tools
  (e.g. shadow `sha256sum` with a `PATH` that lacks it).
- `bin/tingle install` runs at the end of `installer.sh` and edits
  `$HOME/.bashrc`; always use a throwaway `HOME` when testing.
- Adding `install` to `INCLUDES` also ships `install/bootstrap.sh`; that is
  harmless and keeps the rule "the whole folder" simple.
- Do not change the "(future) update flow" message in `installer.sh`; #267
  owns that.
