# Specs: `tingle update` command

Parent issue: #263. This file holds the **shared contracts**, meaning
everything that more than one sub-issue depends on. Each feature spec is
readable on its own, but it must not contradict this file. If they disagree,
this file wins and the feature spec must be fixed.

## 1. Overview

#263 adds a top-level `tingle update` command, alongside `tingle install` and
`tingle uninstall`, that updates an existing **web install** (one with
`tingle.json`). It finishes the "(future) update flow" that
`install/installer.sh` already refers to.

`tingle update` is a **thin command that hands off to the incoming release's
installer**. `shell/update/` resolves the target version, downloads and
verifies the release zip into a temp dir, then `exec`s the **new release's**
`install/installer.sh` in update mode, pointing it at the existing install
folder. The new release's own code therefore decides how it is laid out on
disk, and the code being overwritten is never the code doing the overwriting.

| Feature | Spec | Sub-issue |
|---------|------|-----------|
| Per-file SHA-256 hashes in `MANIFEST` and `tingle.json` | [manifest-hashes.md](manifest-hashes.md) | #264 |
| `install/installer.sh` update mode | [installer-update-mode.md](installer-update-mode.md) | #265 |
| `tingle update` command | [update-command.md](update-command.md) | #266 |
| User guide `docs/guides/update.md` | n/a (rules in section 8) | #267 |
| Cleanup: remove these specs and the index row | n/a | #270 |

## 2. Merge order

The sub-issues are sequential. Each one depends on the one before it:

1. #269: these specs. It lands **first**.
2. #264: manifest hashes.
3. #265: installer update mode.
4. #266: `tingle update` command.
5. #267: user guide.
6. #270: cleanup. It lands **last**.

#264, #265 and #266 must all be merged before the **0.4.0** tag, because the
0.4.0 floor (E2) assumes that hashes, update mode and the `update` command
ship in that release.

## 3. Scope

### In scope

- `tingle update` for **web installs** (those with `tingle.json`): update to
  the latest release, or to a pinned version (downgrade allowed).
- A manifest-driven replace that keeps files the user added.
- `--check`, the "already up to date" no-op, the y/N confirmation and
  `TINGLE_ASSUME_YES`.
- Re-running `tingle install` after the update.
- Checking the downloaded zip against the release's published
  `tingle-<version>.zip.sha256`.
- Per-file SHA-256 hashes in the release `MANIFEST` and in `tingle.json`, so
  local edits to shipped files are detected (starting with 0.4.0).
- `commands/shell.json` help, the `install/installer.sh` message change, and
  the `docs/guides/update.md` user guide.

### Out of scope

- **Git-clone updates (`git pull`):** the follow-up issue #268. Here, a git
  checkout is only detected and pointed at `git pull`.
- Auto-update: no background or periodic checks, and no "new version
  available" notice from other commands.
- Updating dependencies (`jq`, `docker`, the `tingle-linux` image, Python or
  Node packages).
- Converting a git clone into a web install or vice versa.
- Release notes or changelog output (at most the release URL is printed).
- Making `bootstrap.sh` (the `curl | bash` one-liner) update an existing
  install. `tingle update` is the single update entry point. The installer
  keeps refusing and points at it.
- Signature verification (GPG, sigstore). The `.sha256` check catches corrupt
  or truncated downloads, not a compromised GitHub account or release.
- Adding the `.sha256` check to `bootstrap.sh` (first installs).
- Shells other than bash.

### Accepted gap

Installs on 0.3.x or earlier have no `tingle update`, and `bootstrap.sh`
refuses to run over an existing `tingle.json`. This is accepted and not
handled: the only user moves to 0.4.0 by hand.

## 4. File formats

These formats are owned by #264. The later sub-issues depend on them and must
not redefine them.

### `MANIFEST` (in the release zip)

One line per shipped file, in `sha256sum` format:

```text
<64-hex>  <path>
```

- `<64-hex>` is the SHA-256 of the file, followed by **two spaces**
  and the path relative to the zip root.
- Lines are sorted by path with `LC_ALL=C`.
- `MANIFEST` does not list itself.

### `tingle.json` (in the install folder)

```json
{
  "version": "X.Y.Z",
  "repo": "owner/repo",
  "manifest": [
    {"path": "bin/tingle", "sha256": "<64-hex>"}
  ]
}
```

- `version`, `repo` and `manifest` are all required. A `tingle.json` that
  can't be parsed, or that lacks any of them, is corrupt (E3).
- Any code that reads `tingle.json` must still accept the old path-only
  format written by 0.3.x and earlier (`"manifest": ["path", ...]`), treating
  those entries as having no hash.
- Whether an install **tracks hashes** is decided from this **format**
  (whether manifest entries carry a `sha256`), not from the version string.

### Hashing

Hashing must work on macOS and Linux: `sha256sum` when it exists, otherwise
`shasum -a 256`, reusing the `sha_tool` approach from
`scripts/release_cli.sh`. The same portability applies to the per-file hashes
and to the `.sha256` check of the release zip.

### Shared helpers and zip content

- The portable hash helper and the two-format `tingle.json` reader live in
  `install/manifest.sh`. Its function names and outputs are fixed in
  [manifest-hashes.md](manifest-hashes.md) section 3, and #265 and #266 must
  use them rather than re-implement them.
- The release zip must contain `install/` (`installer.sh` and
  `manifest.sh`), since `tingle update` hands off to
  `<tmp>/install/installer.sh`. Today `INCLUDES` does not list it; see
  [manifest-hashes.md](manifest-hashes.md) section 5.

## 5. Env vars and CLI

### Installer update mode (owned by #265)

| Variable | Meaning |
|----------|---------|
| `TINGLE_UPDATE_TARGET` | Install folder to update. Setting it switches `install/installer.sh` into update mode. A leading `~` is expanded and a relative path is made absolute. Without it, the first-install path behaves exactly as before. |
| `TINGLE_UPDATE_FORCE` | `1` overwrites locally edited shipped files (E1). |
| `TINGLE_UPDATE_CLEANUP` | `1` makes update mode remove the source tree (the temp dir it runs from) when it finishes or fails (S3). `tingle update` sets it; when unset (the installer run by hand), the source tree is left alone. |
| `TINGLE_REPO` | Repo recorded in the new `tingle.json`, as today. |
| `TINGLE_VERSION` | Version recorded in the new `tingle.json`, as today. |

### `tingle update` command (owned by #266)

```bash
tingle update [--check] [--force] [<version>]
```

| Input | Meaning |
|-------|---------|
| `<version>` | Pin the target version (skips the API). |
| `--check` | Dry run: print the installed and target versions, and the locally edited shipped files when the install tracks hashes, then exit without changes. |
| `--force` | Go ahead even when shipped files were edited locally. Reaches the installer as `TINGLE_UPDATE_FORCE=1`. |
| `TINGLE_VERSION` | Same as `<version>`. |
| `TINGLE_ASSUME_YES` | Skip the y/N confirmation, the same way as `install/bootstrap.sh`. |

### Test-only hooks (owned by #266)

| Variable | Default |
|----------|---------|
| `TINGLE_RELEASE_API_URL` | `https://api.github.com/repos/<repo>` |
| `TINGLE_RELEASE_BASE_URL` | `https://github.com/<repo>/releases/download` |

They let a local zip, a `file://` URL or a local HTTP server stand in for
GitHub. They are documented as test-only in the script header only, never in
the user guide.

There is no `GITHUB_TOKEN` support, so tingle never has to handle a secret.

## 6. Version rules

- A version is `X.Y.Z` or `X.Y.Z-<suffix>`, with no `v` prefix. Anything else
  is rejected; a pin is rejected before any network call (E6).
- **0.4.0 floor (E2):** `tingle update` can only install 0.4.0 or later. A
  pin below it is refused before downloading anything with
  `tingle update can only install 0.4.0 or later`. The latest release's
  `tag_name` is validated the same way.
- **Latest** means GitHub's latest **stable** release
  (`GET <api>/releases/latest`, `.tag_name` read with `jq`), which skips
  drafts and pre-releases (E10). A pre-release can still be pinned.
- A pin may be older than the installed version: downgrades to 0.4.0 or later
  are allowed.
- An installed `version` of `"unknown"` is always treated as out of date
  (E4).
- When the installed version equals the target, `tingle update` prints
  `tingle is already up to date (<version>)`, changes nothing and exits 0.

## 7. Guarantees and exit codes

- Every abort path **changes nothing** in the install folder.
- An interrupted or failed update leaves the install **fully old**, **fully
  new**, or in a state that **re-running `tingle update` fixes**. It is never
  stuck (see the phases in [installer-update-mode.md](installer-update-mode.md)).
- Files the user added (in neither the old nor the new manifest) are never
  touched.

| Exit | When |
|------|------|
| `0` | Successful update, already up to date, `--check`. |
| non-zero | Every refusal or failure: git checkout, unknown install, corrupt `tingle.json`, invalid pin, pin below 0.4.0, release not found, network failure or rate limit, missing or mismatched checksum, bad zip, install folder not writable, edited files without `--force`, lock held by another run, no `/dev/tty` without `TINGLE_ASSUME_YES`. |

## 8. Rules for #267 (user guide)

#267 must, in one PR:

- add `docs/guides/update.md`, covering:
  - what it updates (web installs made with the `curl | bash` installer), and
    that git checkouts must use `git pull` (#268);
  - usage: `tingle update`, `tingle update <version>` / `TINGLE_VERSION`
    (including downgrades, 0.4.0 or later only), `--check`, `--force`,
    `TINGLE_ASSUME_YES`;
  - that files the user added are kept, while locally edited shipped files
    make it abort unless `--force` is given, and that installs from before
    0.4.0 can't detect such edits;
  - that it is safe to interrupt, and re-running finishes an interrupted
    update;
  - that already-open shells need a restart or `source ~/.bashrc` for the
    new completion;
  - what the common errors mean (no network or rate limit, release not
    found, checksum mismatch, corrupt `tingle.json`);
- **not** document the test-only hooks (`TINGLE_RELEASE_API_URL`,
  `TINGLE_RELEASE_BASE_URL`);
- link the guide from `docs/guides/README.md`;
- cross-link it from `docs/guides/install.md` ("to upgrade later, see
  update.md");
- change the "`tingle.json` already exists … Use the (future) update flow"
  message in `install/installer.sh` so it tells the user to run
  `tingle update` (architect).

The guide must stay consistent with `long_help` in `commands/shell.json` and
the header comment of `shell/update/executor.sh`.

## 9. Edge-case index

The ids below are the ones used in #263. Sub-issues and PRs cite them.

| Id | Case | Owner |
|----|------|-------|
| E1 | Locally edited shipped file: abort and list them unless forced; no hashes recorded means warn and continue. | #265 |
| E2 | Pinned target older than 0.4.0: refused before downloading. | #266 |
| E3 | Corrupt `tingle.json` (unparsable, or `version` / `repo` / `manifest` missing): exit non-zero, change nothing. | #265 and #266 |
| E4 | `version: "unknown"`: always out of date; `--check` shows `unknown → X`. | #266 |
| E5 | Empty manifest (`[]`): nothing deleted, warn that stale files may be left. | #265 |
| E6 | Invalid version pin: rejected before any network call. | #266 |
| E7 | Pinned version doesn't exist (404): `release X not found in <repo>`. | #266 |
| E8 | No network, curl failure or rate limit: exit non-zero, change nothing. | #266 |
| E9 | Zip doesn't unzip or has no `install/installer.sh`: abort. | #266 |
| E9b | `.sha256` missing or mismatched: abort, delete the download. | #266 |
| E10 | Pre-releases: "latest" is the latest stable; a pre-release can be pinned. | #266 |
| E11 | Install folder not writable: fail early, name the folder. | #265 (#266 also checks it before downloading) |
| E12 | Stale files and the directories they leave empty are removed; directories with user files are kept. | #265 |
| E13 | Unsafe manifest paths (absolute or containing `..`): skipped with a warning. | #265 |
| E14 | The install updated is always the folder of the running `bin/tingle`, named in the output. | #266 |
| E15 | Two runs at once: a lock in the install folder refuses the second; a stale lock is cleared. | #265 |

The self-replacement safety rules are split the same way: S1 (hand off with
`exec`) belongs to #266, and S2 (rename, never `cp` in place) and S3 (the
installer cleans up the temp dir when `TINGLE_UPDATE_CLEANUP=1`, which
`tingle update` always sets) belong to #265.
