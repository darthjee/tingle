# Plan: release: add per-file SHA-256 hashes to MANIFEST and tingle.json

Issue: [264-release-add-per-file-sha-256-hashes-to-manifest-and-tingle-json.md](../../issues/264-release-add-per-file-sha-256-hashes-to-manifest-and-tingle-json.md)

## Overview
A new sourced library, `install/manifest.sh`, holds the portable SHA-256
helper, the `MANIFEST` → JSON converter and the two-format `tingle.json`
reader. `scripts/release_cli.sh build` writes `<hash>  <path>` lines into
`MANIFEST` and ships `install/` in the zip. `install/installer.sh` writes
`{path, sha256}` entries into `tingle.json`. `docs/agents/tingle-release-zip.md`
records the new formats. The full spec is
[`docs/agents/specs/update_command/manifest-hashes.md`](../../specs/update_command/manifest-hashes.md).

## Agents involved

- [architect](architect.md): `install/` and `scripts/` (no dedicated specialist)
- [product-owner](product-owner.md): `docs/agents/tingle-release-zip.md`

## Shared contracts

- **`MANIFEST` line:** `<64-hex>  <path>` (lowercase hex, two spaces,
  repo-relative plain path), sorted with `LC_ALL=C` by path, not listing
  `MANIFEST` itself. Consumers split on the first two spaces only.
- **`tingle.json`:**
  `{"version": "X.Y.Z", "repo": "owner/repo", "manifest": [{"path": "...", "sha256": "<64-hex>"}]}`.
  `version`, `repo` and `manifest` are required. The old path-only
  `"manifest": ["path", ...]` (0.3.x and earlier) is still read, as entries
  without a hash. Whether an install tracks hashes depends on this format,
  never on the version string.
- **`install/manifest.sh` functions:** `tingle_sha256 <file>`,
  `tingle_manifest_to_json <MANIFEST>`, `tingle_json_check <tingle.json>`,
  `tingle_json_entries <tingle.json>` (path-only entries print `-` as hash),
  `tingle_json_tracks_hashes <tingle.json>`, with the arguments, output and
  exit status in spec section 3.
- **Zip content:** `INCLUDES` is
  `bin commands completions install shell python node README.md LICENSE`.
