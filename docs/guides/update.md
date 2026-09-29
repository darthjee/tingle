# `tingle update`

Update a web install of tingle to the latest or a pinned release.

## What it does

`tingle update` upgrades (or downgrades) a **web install** of tingle: one made
with the one-line `curl | bash` installer described in the
[Installation](../../README.md#installation) section of the main README. A web
install is recognised by the `tingle.json` file in its folder, which records
the installed version, the GitHub repository it came from, and the list of
files it shipped.

It always updates the folder of the `tingle` you are running, and names that
folder at the start of its output:

```
Updating tingle in /home/you/.tingle
```

It downloads the new release, checks it, and then replaces the shipped files
in place. Files you added to the tingle folder yourself are left alone.

**Git checkouts are not updated.** If you cloned the repository, `tingle
update` refuses and exits non-zero with:

```
tingle update: /path/to/tingle is a git checkout; update it with 'git pull' instead
```

Run `git pull` in your clone instead.

## Prerequisites

- `curl`, `unzip` and `jq`.
- `sha256sum` or `shasum`, to verify the download.
- Network access to GitHub, to download the release (and, when no version is
  pinned, to look up the latest one through the GitHub API).
- Write access to the tingle folder.

## Usage

```
tingle update [--check] [--force] [<version>]
```

### Update to the latest release

```
tingle update
```

Without a version, the target is the latest **stable** GitHub release:
pre-releases and drafts are skipped. When the installed version already
matches it, nothing is changed and tingle prints:

```
tingle is already up to date (0.5.0)
```

Otherwise it prints the installed and target versions, for example
`0.4.0 → 0.5.0`, asks for confirmation, and updates.

### Pin a version

```
tingle update 0.4.1
TINGLE_VERSION=0.4.1 tingle update
```

Pass a version, or set `TINGLE_VERSION`, to install that exact release
instead of the latest one. When both are given, the argument wins over
`TINGLE_VERSION`.

A pinned version:

- must be `X.Y.Z` or `X.Y.Z-<suffix>` (for example `0.5.0` or `0.5.0-rc1`),
  with **no** `v` prefix;
- must be **0.4.0 or later**; older versions are refused with
  `tingle update can only install 0.4.0 or later`;
- may be older than the installed version (a downgrade);
- may be a pre-release.

A pin is checked before any network call, and it skips the GitHub API
lookup, so pinning is also a way around a GitHub API rate limit.

### Options

- `--check` — Dry run. Prints the installed and target versions and, when the
  install tracks file hashes, the shipped files you edited locally. Exits 0
  without downloading or changing anything.
- `--force` — Update even when shipped files were edited locally. Those edits
  are overwritten.

### Confirmation

Before changing anything, `tingle update` asks:

```
Proceed? [y/N]
```

Answer `y` (or `yes`) to go ahead; anything else prints `Aborted.` and exits
non-zero with nothing changed.

Set `TINGLE_ASSUME_YES` (to any value) to skip the prompt. It is **required**
when there is no terminal to ask on, for example in a script or a CI job:

```
TINGLE_ASSUME_YES=1 tingle update
```

## Examples

```
# See what an update would do, without changing anything.
tingle update --check

# Update to the latest stable release.
tingle update

# Install a specific release, e.g. to go back to an earlier version.
tingle update 0.4.0

# Try a pre-release.
tingle update 0.5.0-rc1

# Update even though you edited some shipped files (your edits are lost).
tingle update --force

# Update from a script, without the prompt.
TINGLE_ASSUME_YES=1 tingle update
```

## What it changes and what it keeps

- **The download is verified first.** The release zip is checked against its
  SHA-256 checksum before anything in the tingle folder is replaced. On a
  mismatch the download is deleted and nothing is changed.
- **Shipped files are replaced** with the new release's versions, and files
  that the old release shipped but the new one no longer does are removed
  (along with any directories they leave empty).
- **Files you added are kept.** Anything in the tingle folder that was not
  shipped by a release is never touched, and directories that still hold such
  files are kept.
- **Locally edited shipped files stop the update.** If you changed a file
  that tingle shipped, the update aborts before changing anything and lists
  those files:

  ```
  installer.sh: these shipped files were edited locally:
    bin/tingle
  ```

  Keep a copy of your changes if you need them, then re-run with
  `tingle update --force` to overwrite them. `tingle update --check` lists
  the same files without changing anything.
- **Installs from before 0.4.0 can't detect edits.** Their `tingle.json`
  records no file hashes, so tingle cannot tell whether you edited a shipped
  file. It warns that local edits will be overwritten, and goes on:

  ```
  installer.sh: warning: '/home/you/.tingle/tingle.json' records no file hashes (installed before 0.4.0 or by hand); local edits to shipped files cannot be detected and will be overwritten
  ```

- **`~/.bashrc` is rewired.** As its last step the update runs
  [`tingle install`](install.md) from the updated folder, then prints:

  ```
  tingle in '/home/you/.tingle' was updated to 0.5.0.
  Already-open shells need a restart (or 'source ~/.bashrc') to pick up the new completion.
  ```

## Interrupting it

It is safe to interrupt an update (Ctrl-C, a closed terminal, even a power
loss). `tingle.json` is written last, so until then it still describes the
old version. **Re-running `tingle update` finishes an interrupted update**:
either there is nothing left to do, or it redoes the update from where the
files stand.

While it runs, the update holds a lock in the tingle folder
(`.tingle-update.lock/`). If a previous run was killed and left the lock
behind, the next run notices that its process is gone, clears it with a
warning, and carries on.

## After updating

Shells that are already open keep the old bash completion. Restart them, or
run:

```
source ~/.bashrc
```

## Troubleshooting

Every failure below exits non-zero. Unless stated otherwise, nothing in the
tingle folder was changed.

- **No network:** `could not reach ... to find the latest release (network
  failure)` or `could not download ... (network failure); nothing was
  changed`. Check your connection and try again. If only the latest-release
  lookup fails, pin a version: `tingle update X.Y.Z`.
- **GitHub rate limit:** `the GitHub API rate limit was hit (HTTP 403) while
  looking up the latest release` (or HTTP 429). Wait and try again, or pin a
  version to skip the lookup: `tingle update X.Y.Z`. If it is hit while
  downloading the zip, try again later.
- **Release not found:** `release <version> not found in <repo>`. The version
  you pinned does not exist (or has no release zip). Check the spelling and
  the list of releases on GitHub.
- **Invalid pin:** `tingle update: invalid version '<version>' (expected
  X.Y.Z or X.Y.Z-<suffix>, with no 'v' prefix)`. Drop any `v` prefix, e.g.
  `tingle update 0.5.0` rather than `tingle update v0.5.0`.
- **Pin older than 0.4.0:** `tingle update can only install 0.4.0 or later`.
  Releases before 0.4.0 can't be installed this way; pick 0.4.0 or later.
- **Checksum mismatch:** `checksum mismatch for tingle-<version>.zip
  (expected '...', got '...'); the download was deleted and nothing was
  changed`. The download was corrupted or tampered with. Try again; if it
  keeps failing, do not install that release by other means.
- **Corrupt `tingle.json`:** `tingle update: <folder>/tingle.json is corrupt
  (it can't be parsed, or 'version', 'repo' or 'manifest' is missing);
  nothing was changed`. The file was edited or damaged. Reinstall tingle with
  the web installer into a fresh folder.
- **Not a web install:** `can't tell how tingle was installed in <folder>
  (no tingle.json and not a git checkout); nothing was changed`. Reinstall
  with the web installer to be able to use `tingle update`.
- **Git checkout:** `<folder> is a git checkout; update it with 'git pull'
  instead`. Run `git pull` in your clone.
- **Folder not writable:** `the install folder <folder> is not writable`.
  Fix the folder's permissions, or run the update as the user who owns it.
- **Another update in progress:** `another update of '<folder>' is in
  progress (pid <pid> holds '<folder>/.tingle-update.lock'); nothing was
  changed`. Wait for the other update to finish. A lock left behind by a
  process that is no longer running is cleared automatically.
- **No terminal:** `tingle update: no /dev/tty available to confirm; re-run
  with TINGLE_ASSUME_YES=1 to skip the prompt`. Set `TINGLE_ASSUME_YES` when
  running without a terminal.
- **Locally edited shipped files:** `update aborted; nothing was changed`,
  after the list of edited files. See
  [What it changes and what it keeps](#what-it-changes-and-what-it-keeps).
- **Update done, but `~/.bashrc` not rewired:** `tingle <version> was
  installed in '<folder>', but wiring ~/.bashrc failed; re-run
  '<folder>/bin/tingle install' by hand`. The new version is installed; run
  that command yourself to finish.
