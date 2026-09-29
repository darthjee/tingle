# Spec: `tingle update` command

Sub-issue: #266. Parent issue: #263. Shared contracts:
[README.md](README.md), which wins if this file disagrees with it.

## 1. Goal

Add a top-level `tingle update` command, alongside `tingle install` and
`tingle uninstall`, that updates a **web install** (one with `tingle.json`) to
the latest release, or to a pinned one. It is deliberately **thin**: it
resolves the target version, downloads and verifies the release zip, then
hands off to the **new release's** `install/installer.sh` in update mode
([installer-update-mode.md](installer-update-mode.md)), which does the actual
replacement.

This sub-issue depends on #264 (hashes and the `install/manifest.sh` helpers)
and #265 (installer update mode). It must be merged before the 0.4.0 tag,
since `tingle update` ships in 0.4.0.

It covers E2, E4, E6, E7, E8, E9, E9b, E10 and E14, checks E3 and E11 before
downloading, and owns the safety rule S1 and the test-only hooks.

## 2. CLI

```bash
tingle update [--check] [--force] [<version>]
```

| Input | Meaning |
|-------|---------|
| `<version>` | Pin the target version, `X.Y.Z` or `X.Y.Z-<suffix>`, no `v` prefix. It skips the API. It may be older than the installed version (downgrade), and may be a pre-release. |
| `TINGLE_VERSION` | Same as `<version>`. When both are given, the argument wins. |
| `--check` | Dry run: print the installed and target versions, and the locally edited shipped files when the install tracks hashes. Then exit 0 without changing anything. |
| `--force` | Go ahead even when shipped files were edited locally (E1). Passed to the installer as `TINGLE_UPDATE_FORCE=1`. |
| `TINGLE_ASSUME_YES` | When set (to any value), skip the y/N confirmation, the same way as `install/bootstrap.sh`. |

These messages are fixed and must be printed as written:

- `tingle is already up to date (<version>)`
- `release <version> not found in <repo>`
- `tingle update can only install 0.4.0 or later`

### Example sessions

The wording below is illustrative, except for the fixed messages above.

Already up to date:

```console
$ tingle update
Updating tingle in /home/me/.tingle
tingle is already up to date (0.4.1)
```

`--check` with edited files:

```console
$ tingle update --check
Updating tingle in /home/me/.tingle
0.4.0 → 0.4.1
Locally edited shipped files (use --force to overwrite them):
  commands/shell.json
```

`--check` on a standalone install:

```console
$ tingle update --check
Updating tingle in /home/me/.tingle
unknown → 0.4.1
```

A pin (downgrade):

```console
$ tingle update 0.4.0
Updating tingle in /home/me/.tingle
0.4.1 → 0.4.0
Proceed? [y/N] y
...
```

A refused pin:

```console
$ tingle update 0.3.0
tingle update can only install 0.4.0 or later
$ echo $?
1
```

## 3. Flow

`shell/update/executor.sh` runs these steps in order. Every step before the
handoff that fails exits non-zero with nothing changed.

### 3.1 Detect the install (E3, E14)

- **Which install (E14):** always the folder of the running `bin/tingle`,
  resolved from the executor's own location (`$(dirname "$0")/../..`, as in
  `shell/uninstall/executor.sh`). The output names that folder.
- **Web install:** `<folder>/tingle.json` exists. It must pass
  `tingle_json_check` (from `install/manifest.sh`): if it can't be parsed, or
  `version`, `repo` or `manifest` is missing, exit non-zero and change nothing
  (E3). The installed version and the repo are read from it.
- **Git checkout:** no `tingle.json`, and the folder is a git checkout (a
  `.git` entry at its root). Print that this is a git checkout and that it
  should be updated with `git pull`, then exit non-zero. A real git-clone
  update path is #268.
- **Unknown:** neither. Exit non-zero and explain that tingle cannot tell how
  it was installed.
- **Writable (E11):** the install folder must be writable. This is checked
  here, before downloading, failing early and naming the folder. The installer
  checks it again in preflight.

### 3.2 Resolve the target (E2, E6, E7, E8, E10)

- **Pin:** `<version>` or `TINGLE_VERSION`. It is validated **before any
  network call**: it must match `X.Y.Z` or `X.Y.Z-<suffix>` (E6) and be 0.4.0
  or later (E2). A pin skips the API and goes straight to the release
  download URL. It is also the fallback when the API is unavailable.
- **Latest:** `GET <api>/releases/latest` (unauthenticated), reading
  `.tag_name` with `jq`. That endpoint skips drafts and pre-releases, so
  "latest" is the latest **stable** release (E10). `tag_name` is validated
  like a pin (E6, E2).
- **Errors (E8):** a rate limit (HTTP 403 or 429), a network failure or an
  unexpected response prints a clear message suggesting a pinned version, then
  exits non-zero with nothing changed. The unauthenticated limit of 60
  requests per hour per IP is enough for personal use.
- There is no `GITHUB_TOKEN` support, so tingle never has to handle a secret.

### 3.3 Up to date and `--check` (E4)

- When the installed version equals the target, print
  `tingle is already up to date (<version>)`, change nothing and exit 0.
- An installed version of `"unknown"` is always treated as out of date (E4).
- `--check` prints the installed and target versions (`unknown → X` when the
  installed version is unknown). When the install tracks hashes
  (`tingle_json_tracks_hashes`), it also lists the shipped files whose hash
  differs from the one recorded in `tingle.json`. Then it exits 0 without
  downloading or changing anything.

### 3.4 Confirmation

- Before changing anything, ask a y/N prompt on `/dev/tty`. Anything but a
  yes aborts with nothing changed.
- `TINGLE_ASSUME_YES` skips the prompt.
- With no `/dev/tty` and no `TINGLE_ASSUME_YES`, abort with a hint to set
  `TINGLE_ASSUME_YES`.

### 3.5 Download and verify (E7, E8, E9, E9b)

- Create a temp dir with `mktemp -d`, and download into it:
  - `<base>/<version>/tingle-<version>.zip`
  - `<base>/<version>/tingle-<version>.zip.sha256`
- A 404 on the zip prints `release <version> not found in <repo>` (E7). A
  network failure or rate limit behaves as in 3.2 (E8).
- **Checksum (E9b):** the `.sha256` asset can't be downloaded, or its hash
  doesn't match the zip's hash (computed with `tingle_sha256`): abort, delete
  the download, change nothing.
- **Unpack (E9):** unzip at the root of the temp dir. A zip that doesn't
  unzip, or that has no `install/installer.sh`, aborts with nothing changed.
- The download and unzip logic is reused from `install/bootstrap.sh`.
- Because the executor sets no trap (S1), every failure in this step removes
  the temp dir explicitly before exiting.

### 3.6 Hand off (S1)

The last step is:

```bash
TINGLE_UPDATE_TARGET="<folder>" \
TINGLE_REPO="<repo from tingle.json>" \
TINGLE_VERSION="<target version>" \
exec "<tmp>/install/installer.sh"
```

with `TINGLE_UPDATE_FORCE=1` also set when `--force` was given.

- **S1:** nothing runs after the `exec`, and `executor.sh` sets no cleanup
  trap of its own (an `exec` drops traps). The dispatch chain `bin/tingle` →
  `exec shell/update/main.sh` → `exec executor.sh` already uses `exec`, so
  after the handoff no process is reading any script inside the install
  folder.
- The installer cleans up the temp dir (S3,
  [installer-update-mode.md](installer-update-mode.md)).
- An older `tingle update` only works against releases whose `installer.sh`
  has update mode. This is fine, because update mode ships in the same release
  as the `update` command, and the 0.4.0 floor (E2) excludes older targets.

## 4. Test-only hooks

| Variable | Default |
|----------|---------|
| `TINGLE_RELEASE_API_URL` | `https://api.github.com/repos/<repo>` |
| `TINGLE_RELEASE_BASE_URL` | `https://github.com/<repo>/releases/download` |

`<api>` and `<base>` in section 3 are these values. They let a local zip, a
`file://` URL or a local HTTP server (`python3 -m http.server`) stand in for
GitHub. They are documented as test-only in the header of
`shell/update/executor.sh`, and never in the user guide or `long_help`.

## 5. Layout

- `shell/update/main.sh` and `shell/update/executor.sh`, with the same
  flow-verb layout as `shell/install/` and `shell/uninstall/` (`main.sh run`
  `exec`s `executor.sh`).
- A new `update` entry in `commands/shell.json` (`path`
  `shell/update/main.sh`), with a `short_help` and a `long_help` covering the
  usage, `--check`, `--force`, the version pin, `TINGLE_VERSION`,
  `TINGLE_ASSUME_YES`, and the git-checkout message.
- The hash helper and the two-format `tingle.json` reader come from
  `install/manifest.sh` (#264), sourced from the install folder.

## 6. Rejected alternatives

- **`shell/update/executor.sh` does everything itself:** the old installed
  code would decide how a new release is laid out, the script would overwrite
  itself while running, and the download and manifest code would be
  duplicated from `install/`.
- **Re-run `curl … bootstrap.sh | bash` with an overwrite flag:** it isn't a
  `tingle` command, it ignores the install path and version in `tingle.json`,
  and `--check` is awkward.
- **Wipe and reinstall:** it loses files the user added.
- **Scraping the redirect of `https://github.com/<repo>/releases/latest`:** no
  rate limit and no `jq`, but it relies on a web page, not an API contract, so
  it could break without warning.
- **Downloading from `releases/latest/download/…`:** not possible, because the
  asset name contains the version (`tingle-<version>.zip`).
- **`GITHUB_TOKEN` support:** not added, so tingle never handles a secret. It
  can be added later if the rate limit ever becomes a problem.

## 7. Testing

There is no shell test framework, and none is added. Use the test hooks with
zips built by `scripts/release_cli.sh build <tag>`, served from a local folder
or `python3 -m http.server`, and a throwaway `HOME`:

- An end-to-end update from a 0.4.0-or-later install to a newer build.
- Already up to date, `--check`, a pin, and a downgrade to 0.4.0 or later.
- A pin below 0.4.0 and an invalid pin are refused before any download.
- Refused without a TTY and without `TINGLE_ASSUME_YES`.
- A 404, a checksum mismatch, no network, a corrupt `tingle.json` and an
  unwritable folder leave the install untouched.
- An edited file aborts, and `--force` goes through.
- A git checkout gets the `git pull` message, and an unknown install is
  refused.
- `shellcheck` passes.

## 8. Permanent home

Before #270 deletes this spec, these docs must cover it:

- The header comment of `shell/update/executor.sh`: the flow, S1, and the
  test-only hooks.
- `long_help` of `update` in `commands/shell.json`: the CLI.
- `docs/guides/update.md` (#267): the user-visible behaviour, per README
  section 8.
