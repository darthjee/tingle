# Add the install/manifest.sh library

Create `install/manifest.sh`, a **sourced** library: a `#!/usr/bin/env bash`
line is fine for editors/shellcheck, but it has no `set -e`/`set -u` of its
own, runs nothing at load time and defines only functions. Its header comment
documents every function, its arguments, stdout and exit status (spec section
7), plus the `MANIFEST` line format and the rule "split on the first two
spaces only".

Functions (interface fixed by spec section 3; do not rename):

- `tingle_sha256 <file>`: fail (non-zero) when `<file>` is not a readable
  regular file. Otherwise hash it with `sha256sum` when on `PATH`, else
  `shasum -a 256`, **reading from stdin** (`< "$file"`) so the tool never
  prints its `\`-escaped form for special names, and print only the 64-hex
  field.
- `tingle_manifest_to_json <MANIFEST>`: print `[]` when the file is missing or
  has no non-blank lines. Otherwise read it line by line
  (`IFS= read -r`, also handling a last line without a trailing newline),
  skip blank lines, split each line with `hash=${line%%  *}` /
  `path=${line#*  }`, and fail (non-zero, message on stderr naming the line)
  when the separator is missing, the hash is not 64 lowercase hex or the path
  is empty. JSON-escape the path (backslashes first, then double quotes) and
  print a pretty array in the same layout `installer.sh` uses today:
  ```text
  [
      {"path": "LICENSE", "sha256": "<hex>"},
      {"path": "bin/tingle", "sha256": "<hex>"}
    ]
  ```
  (entries indented four spaces, closing bracket two spaces, so it nests
  under `"manifest": ` in `tingle.json`). Must not need `jq`.
- `tingle_json_check <tingle.json>`: `jq -e` that the file parses and is an
  object with `version`, `repo` and `manifest` keys, `manifest` being an
  array. Silent; non-zero otherwise (E3), including when `jq` is missing.
- `tingle_json_entries <tingle.json>`: return non-zero when
  `tingle_json_check` fails. Otherwise print one `<hash>  <path>` line per
  entry: string entries (old format) print `-` as hash; object entries print
  `.sha256 // "-"` and `.path`. Use `jq -r`.
- `tingle_json_tracks_hashes <tingle.json>`: `0` only when
  `tingle_json_check` passes, the manifest is non-empty and every entry is an
  object with a string `sha256`; non-zero otherwise (path-only, mixed or
  `[]`).

## Files to Change
- `install/manifest.sh` — new sourced helper library.
