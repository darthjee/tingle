# Write {path, sha256} entries in tingle.json

In `install/installer.sh`:

- Source the sibling library right after `SCRIPT_DIR` is resolved:
  `. "$SCRIPT_DIR/manifest.sh"` (with a `# shellcheck source=manifest.sh`
  directive). Fail with a clear `installer.sh:` message if it is missing.
- Replace the inline `awk` block with
  `manifest_json="$(tingle_manifest_to_json "$SOURCE_ROOT/MANIFEST")"`; a
  missing or empty `MANIFEST` still yields `[]`. Run the conversion **before**
  `mkdir -p "$target"` / `cp -R`, so a malformed `MANIFEST` aborts with an
  `installer.sh:` message and nothing copied.
- Do not call any `tingle_json_*` reader here, so `jq` stays optional on the
  first-install path.
- Update the header comment: document the `tingle.json` schema
  (`version`, `repo`, `manifest: [{path, sha256}]`), that `manifest` is `[]`
  without a `MANIFEST`, that 0.3.x and earlier wrote a path-only
  `manifest: ["path", ...]` which readers still accept, and that the script
  depends on its sibling `install/manifest.sh`.

Verify with an unpacked build: `HOME=$(mktemp -d)`, run
`<unpacked>/install/installer.sh </dev/null` (default target under the
throwaway `HOME`), then check `jq . <target>/tingle.json` and compare each
entry's `sha256` against `tingle_sha256 <target>/<path>`. Also run
`tingle_json_entries` / `tingle_json_tracks_hashes` on that file, on a
hand-written 0.3.x-style path-only file, and `tingle_json_check` on a
corrupt one.

## Files to Change
- `install/installer.sh` — source `manifest.sh`, new manifest JSON, header comment.
