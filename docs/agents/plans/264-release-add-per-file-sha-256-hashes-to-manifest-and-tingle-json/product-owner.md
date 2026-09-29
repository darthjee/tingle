# Product-owner Plan: release: add per-file SHA-256 hashes to MANIFEST and tingle.json

Main plan: [plan.md](plan.md)

## Shared contracts

Relies on the architect's contracts in [plan.md](plan.md#shared-contracts):
the `MANIFEST` line format, the `tingle.json` schema (including the old
path-only format still being read) and `install` in `INCLUDES`. Document them
as the architect implements them; do not redefine them.

## Implementation Steps

### Step 1 — Update the release zip contract doc
In `docs/agents/tingle-release-zip.md` (spec section 7, "Permanent home"):
- **`INCLUDES` allowlist:** add `install` to the listed top-level entries.
- **`MANIFEST`:** replace "Sorted (`LC_ALL=C`) list of every packaged
  repo-relative path" with the `sha256sum`-format line `<64-hex>  <path>`
  (two spaces), still `LC_ALL=C`-sorted by path and not listing itself;
  mention that consumers split on the first two spaces only.
- **New `tingle.json` entry:** what `install/installer.sh` writes into the
  install folder (`version`, `repo`, `manifest: [{path, sha256}]`, `[]`
  without a `MANIFEST`), that 0.3.x and earlier wrote a path-only `manifest`
  which readers still accept as entries without a hash, that "tracks hashes"
  is decided from the format and not the version, and that the helpers live
  in `install/manifest.sh`.

## Files to Change
- `docs/agents/tingle-release-zip.md` — `INCLUDES`, `MANIFEST` format, new `tingle.json` entry.

## Notes
- Leave `docs/agents/specs/update_command/` alone; #270 deletes it.
- No user guide change here; #267 owns `docs/guides/update.md`.
