# Spec: per-file SHA-256 hashes in `MANIFEST` and `tingle.json`

Sub-issue: #264. Parent issue: #263. Shared contracts:
[README.md](README.md), which wins if this file disagrees with it.

## 1. Goal

Record a SHA-256 hash for every shipped file, both in the release zip's
`MANIFEST` and in the `tingle.json` that the web installer writes. Installer
update mode (#265) uses these hashes to detect local edits to shipped files
(E1) and to recover from an interrupted update, and `tingle update --check`
(#266) uses them to list edited files.

This sub-issue can land on its own, since it only improves first installs. It
must be merged before the 0.4.0 tag, because 0.4.0 is documented as the first
release whose installs carry hashes.

This sub-issue **owns** the `MANIFEST` line format and the `tingle.json`
schema (README section 4). #265 and #266 depend on them and must not redefine
them.

## 2. Behaviour

### `scripts/release_cli.sh build`

- `MANIFEST` is written in `sha256sum` format: one `<64-hex>  <path>` line per
  packaged file (hash, two spaces, repo-relative path).
- The file list is unchanged: the `INCLUDES` allowlist resolved through
  `git ls-files`, pruned as today, sorted with `LC_ALL=C`, and not listing
  `MANIFEST` itself.
- The hash is computed with the existing `sha_tool` helper
  (`sha256sum`, falling back to `shasum -a 256`), over the same file that is
  zipped.

Example `MANIFEST`:

```text
3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8550  LICENSE
9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08  README.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  bin/tingle
```

### `install/installer.sh` (first install)

- It parses the new `MANIFEST` and writes `{path, sha256}` entries into
  `<target>/tingle.json`, escaping JSON as it already does (backslashes and
  double quotes).
- A missing `MANIFEST` (a hand-built tree) or an empty one writes
  `"manifest": []`, as today.

Example `tingle.json`:

```json
{
  "version": "0.4.0",
  "repo": "darthjee/tingle",
  "manifest": [
    {"path": "LICENSE", "sha256": "3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8550"},
    {"path": "README.md", "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"},
    {"path": "bin/tingle", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
  ]
}
```

### Reading old installs

Any code that reads `tingle.json` must still accept the old path-only format
written by 0.3.x and earlier:

```json
{
  "version": "0.3.0",
  "repo": "darthjee/tingle",
  "manifest": ["LICENSE", "README.md", "bin/tingle"]
}
```

Those entries are treated as having no hash. Whether an install **tracks
hashes** is decided from this format, not from the version string.

## 3. Shared helpers

#265 (run from the unpacked release in a temp dir) and #266 (run from the
install folder) both consume these helpers, so their location and interface
are fixed here.

- **Location:** `install/manifest.sh`, a sourced library (no shebang
  behaviour, no `set -e` of its own, no side effects when sourced). Scripts
  source it relative to their own location: `installer.sh` from its sibling
  file, `shell/update/executor.sh` from `<tingle root>/install/manifest.sh`.
- **Dependencies:** `sha256sum` or `shasum -a 256` for hashing, and `jq` for
  reading `tingle.json`. `jq` is already required by `bin/tingle` and by
  update mode. The first-install path must not call the `tingle.json` reader,
  so `jq` stays optional there.

| Function | Arguments | Output (stdout) | Exit status |
|----------|-----------|-----------------|-------------|
| `tingle_sha256` | `<file>` | The file's 64-hex SHA-256, alone on one line. | Non-zero when the file can't be read. |
| `tingle_manifest_to_json` | `<MANIFEST file>` | The JSON array written as `tingle.json`'s `manifest` (`[{path, sha256}, ...]`), or `[]` when the file is missing or empty. | Non-zero on a malformed line. |
| `tingle_json_check` | `<tingle.json>` | Nothing. | `0` when the file parses and has `version`, `repo` and `manifest`; non-zero otherwise (E3). |
| `tingle_json_entries` | `<tingle.json>` | One `<hash>  <path>` line per manifest entry, in `MANIFEST` format. A path-only entry prints `-` as its hash. | Non-zero when `tingle_json_check` fails. |
| `tingle_json_tracks_hashes` | `<tingle.json>` | Nothing. | `0` when the manifest has at least one entry and every entry carries a `sha256`; non-zero otherwise (path-only format or `[]`). |

Every consumer must split a `<hash>  <path>` line on the **first two spaces
only**: the hash is the text before them, and the path is everything after
them, including any further spaces.

## 4. Edge cases

- **Paths containing spaces:** allowed. The line format splits on the first
  two spaces only, so `abc…  docs/my file.md` has the path `docs/my file.md`.
- **Paths needing JSON escaping:** backslashes and double quotes in a path are
  escaped when writing `tingle.json`, and unescaped by `jq` when reading.
- **Escaped `sha256sum` output:** `MANIFEST` must hold the plain path, never
  the `\`-prefixed form `sha256sum` prints for names containing a backslash
  or a newline. Paths containing a newline are not supported.
- **Empty `MANIFEST`:** `tingle.json` gets `"manifest": []`. That install does
  not track hashes, and update mode handles it as E5.

## 5. Known gap: `install/` is not in the release zip

The whole #263 design hands off to `<tmp>/install/installer.sh` from the
unpacked zip, and E9 aborts when the zip has none. Today `INCLUDES` in
`scripts/release_cli.sh` is `bin commands completions shell python node
README.md LICENSE`: it does not list `install`, and the published
`tingle-0.3.0.zip` indeed has no `install/` folder. The helper above also
lives under `install/`.

`install` must be added to `INCLUDES` (and listed in `MANIFEST`) before the
0.4.0 tag. #264 is the sub-issue that already changes `release_cli.sh`, so it
must make this change unless the parent issue #263 assigns it elsewhere.

## 6. Testing

There is no shell test framework, and none is added. Verify by hand:

- `scripts/release_cli.sh build <tag>`: the zip's `MANIFEST` has
  `<hash>  <path>` lines, sorted with `LC_ALL=C`, not listing itself, and each
  hash matches the zipped file.
- Run the unpacked `install/installer.sh` against a throwaway `HOME` and
  target: `tingle.json` has `{path, sha256}` entries matching the installed
  files.
- The reader (`tingle_json_entries`, `tingle_json_tracks_hashes`) handles
  both an old path-only `tingle.json` and a new one, and
  `tingle_json_check` rejects a corrupt one.
- Hashing works with both `sha256sum` and `shasum -a 256`.
- `shellcheck` passes on the changed and new scripts.

## 7. Permanent home

Before #270 deletes this spec, these docs must cover it:

- `docs/agents/tingle-release-zip.md`: the `MANIFEST` bullet (today "path-only
  list") describes the `<hash>  <path>` format, still `LC_ALL=C`-sorted by
  path and not listing itself; a new entry describes the `tingle.json` schema,
  including the old path-only format still being read; and the `INCLUDES`
  list shows `install`.
- The header comment of `scripts/release_cli.sh`: the `MANIFEST` format.
- The header comment of `install/installer.sh`: the `tingle.json` schema.
- The header comment of `install/manifest.sh`: every function, its arguments
  and its output.
