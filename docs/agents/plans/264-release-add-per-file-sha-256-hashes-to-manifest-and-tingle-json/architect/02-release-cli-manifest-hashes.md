# Hash files in MANIFEST and ship install/

In `scripts/release_cli.sh`:

- Add `install` to `INCLUDES` (keep the alphabetical-ish order:
  `bin commands completions install shell python node README.md LICENSE`),
  so the zip carries `install/installer.sh` and `install/manifest.sh`.
  `resolve_files` and the prune/sensitive guards stay as they are.
- In `cmd_build`, replace `echo "$files" > "$manifest"` with a loop over
  `$files` (already `LC_ALL=C`-sorted) that writes one
  `<hash>  <path>` line per file, hashing via the existing `sha_tool` helper
  over stdin (`$(sha_tool) < "$f" | cut -d' ' -f1`, keeping the existing
  `SC2046` disable style) so the output is the plain path and never the
  `\`-escaped form. Hashes are computed from the working-tree files that
  `zip -@` packages in the next line, so they match the zipped content.
  Fail the build if any hash comes out empty.
- Update the header comment: the `Zip content` paragraph lists `install`,
  and describes `MANIFEST` as `sha256sum`-format `<64-hex>  <path>` lines,
  `LC_ALL=C`-sorted by path, not listing itself.

Verify: build a throwaway tag, `unzip -p` the `MANIFEST`, and check a few
hashes against `unzip -p <zip> <path> | shasum -a 256`.

## Files to Change
- `scripts/release_cli.sh` — `INCLUDES`, hashed `MANIFEST`, header comment.
