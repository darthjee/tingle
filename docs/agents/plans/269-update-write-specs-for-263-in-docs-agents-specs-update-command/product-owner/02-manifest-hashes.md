# Write manifest-hashes.md (#264)
Create `docs/agents/specs/update_command/manifest-hashes.md`, linking #264.
It covers:
- **Behaviour:**
  - `scripts/release_cli.sh build` writes `MANIFEST` as `<hash>  <path>`
    lines, reusing its `sha_tool`.
  - `install/installer.sh` (first install) writes `{path, sha256}` entries to
    `tingle.json`.
  - Examples of both files.
- **Shared helpers:** a portable hash helper (`sha256sum`, falling back to
  `shasum -a 256`), and a `tingle.json` manifest reader that accepts both
  formats. Both must live where #265 and #266 can source them (for example
  a small helper under `install/`). The spec must fix the location and the
  function names/outputs, since two later sub-issues consume them.
- **Edge cases:** a path containing spaces (the line format splits on the
  first two spaces only), JSON escaping of paths, and an empty `MANIFEST`.
- **Testing:** hashes in the built zip match its files, a first install
  records matching hashes, the reader handles both formats, and `shellcheck`
  passes.
- **Permanent home:** `docs/agents/tingle-release-zip.md` (the `MANIFEST`
  bullet, which today says "path-only list"; add the `tingle.json` schema),
  and the header comments of `scripts/release_cli.sh` and
  `install/installer.sh`.

## Files to Change
- `docs/agents/specs/update_command/manifest-hashes.md`: new.
