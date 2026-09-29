# Download, verify and hand off
**Download (spec 3.5, E7, E8, E9, E9b):** `WORK="$(mktemp -d)"`, with
**no trap**. Add a `fail` helper that runs `rm -rf "$WORK"`, prints the
message to stderr and exits 1. Use it for every error from here on.
`<base>` is
`${TINGLE_RELEASE_BASE_URL:-https://github.com/<repo>/releases/download}`.

- Fetch `<base>/<v>/tingle-<v>.zip` with curl `-L -sS -w '%{http_code}'`.
  A 404 (or a failed `file://` fetch) prints exactly
  `release <v> not found in <repo>`. 403/429 is a rate limit, and any other
  failure is a network error, both handled as in step 03.
- Fetch `<base>/<v>/tingle-<v>.zip.sha256`. If it's missing, or its first
  field isn't equal to `tingle_sha256` of the zip, `fail` with a checksum
  error.
- Download both files into `$WORK`, then `unzip -q` at the root of `$WORK`
  (a failure is a bad zip). A missing or non-executable
  `$WORK/install/installer.sh` fails too.

**Hand off (spec 3.6, S1):** the last line is

```bash
TINGLE_UPDATE_TARGET="$TINGLE_FOLDER" TINGLE_UPDATE_CLEANUP=1 \
TINGLE_REPO="$repo" TINGLE_VERSION="$target" \
exec "$WORK/install/installer.sh"
```

with `TINGLE_UPDATE_FORCE=1` exported first when `--force` was given.
The installer's `SOURCE_ROOT` is the parent of `install/`, i.e. `$WORK`
itself, and with `TINGLE_UPDATE_CLEANUP=1` its EXIT trap
(`update_on_exit` in `install/update.sh`) runs `rm -rf "$SOURCE_ROOT"`. That
is why the zip is unpacked at the root of `$WORK`: the whole temp dir,
downloaded zip and `.sha256` included, is removed once the update finishes or
fails. Update mode is manifest-driven, so the extra zip and `.sha256` files
in `$WORK` are never copied into the install.

## Files to Change
- `shell/update/executor.sh` — download, checksum, unzip, `exec` handoff.
