# `tingle update`

Update tingle: a web install to the latest or a pinned release, or a git
checkout with `git pull`.

## What it does

`tingle update` always updates the folder of the `tingle` you are running, and
names that folder at the start of its output:

```
Updating tingle in /home/you/.tingle
```

How it updates depends on how that folder was installed:

- **Web install**: one made with the one-line `curl | bash` installer
  described in the [Installation](../../README.md#installation) section of the
  main README. A web install is recognised by the `tingle.json` file in its
  folder, which records the installed version, the GitHub repository it came
  from, and the list of files it shipped. `tingle update` downloads the new
  release, checks it, and then replaces the shipped files in place. Files you
  added to the tingle folder yourself are left alone. Most of this guide
  describes this case.
- **Git checkout**: a clone of the repository. `tingle update` fast-forwards
  the current branch with `git pull --ff-only` and then re-runs
  `tingle install`. See [Updating a git checkout](#updating-a-git-checkout).

`tingle update` first shipped in 0.4.0. An install on 0.3.x or earlier has no
`tingle update`, and the one-line installer refuses to run over a folder that
already has a `tingle.json`, so moving such an install to 0.4.0 is a manual
step: remove the old tingle folder (keep a copy of any files you added to it)
and run the one-line installer again.

## Prerequisites

- A tingle folder on 0.4.0 or later (see [What it does](#what-it-does)).
- Write access to the tingle folder.
- For a **git checkout**: `git`, and network access to the branch's upstream
  remote.
- For a **web install** only:
  - `curl`, `unzip` and `jq`;
  - `sha256sum` or `shasum`, to verify the download;
  - network access to GitHub, to download the release (and, when no version
    is pinned, to look up the latest one through the GitHub API).

## Usage

```
tingle update [--check] [--force] [<version>]
```

### Update to the latest release

```
tingle update
```

On a web install, without a version, the target is the latest **stable** GitHub release:
pre-releases and drafts are skipped. When the installed version already
matches it, nothing is changed and tingle prints:

```
tingle is already up to date (0.5.0)
```

and exits 0.

Otherwise it prints the installed and target versions, for example
`0.4.0 → 0.5.0`, asks for confirmation, and updates.

If `tingle.json` records the installed version as `unknown` (for example when
tingle was installed by running the installer from a checkout without setting
`TINGLE_VERSION`), the install is always treated as out of date, and the
versions line reads `unknown → 0.5.0`.

On a git checkout, the same command pulls the current branch instead; see
[Updating a git checkout](#updating-a-git-checkout).

### Pin a version (web installs only)

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

Pins are refused on a git checkout; check out a tag yourself instead (see
[Updating a git checkout](#updating-a-git-checkout)).

### Options

- `--check` — Dry run. On a web install, prints the installed and target
  versions (`unknown → X` when the installed version is unknown) and, when
  the install tracks file hashes, the shipped files you edited locally. When
  the install is already up to date, it prints the up-to-date line instead. On a git checkout, fetches the upstream and reports how far
  behind and ahead the branch is. Either way it exits 0 without changing
  anything in the tingle folder.
- `--force` — Web installs only. Update even when shipped files were edited
  locally. Those edits are overwritten. It is refused on a git checkout.

### Confirmation (web installs only)

Before changing anything on a web install, `tingle update` asks:

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

A git checkout is updated without a prompt, and `TINGLE_ASSUME_YES` is ignored
there.

## Updating a git checkout

If the tingle folder is a clone of the repository, `tingle update`:

1. checks that the checkout is safe to update (see the refusals below);
2. fetches the current branch's upstream (for example `origin/main`);
3. runs `git pull --ff-only` on the current branch, showing git's own output;
4. re-runs [`tingle install`](install.md) from the freshly pulled folder, so
   `~/.bashrc` and the bash completion pick up the new version. The exit
   status of `tingle update` is the exit status of that `tingle install`.

There is no confirmation prompt. Only `git` is needed; `curl`, `unzip` and
`jq` are not. Untracked files (files git does not know about) do not stop the
update and are left alone.

When the branch is not behind its upstream, nothing is pulled and tingle
prints (with your branch and its short commit hash):

```
tingle is already up to date (main, 1a2b3c4)
```

### Checking a git checkout

```
tingle update --check
```

This fetches the upstream and prints how the branch compares with it, without
pulling or re-running `tingle install`:

```
main: 3 commit(s) behind, 0 ahead of origin/main
```

When the branch is not behind, the up-to-date line above is printed instead.
It exits 0.

### When a git checkout is not updated

In each case below, tingle prints the message (prefixed with
`tingle update: `, on stderr), exits 1, and changes nothing. `<folder>` is the
tingle folder, `<branch>` the current branch and `<upstream>` its upstream.

- **Uncommitted changes.** Staged or unstaged changes to tracked files:

  ```
  tingle update: <folder> has uncommitted changes; commit or stash them, then re-run; nothing was changed
  ```

  Commit your changes, or put them aside with `git stash`, then re-run
  `tingle update` (and `git stash pop` afterwards if you stashed).

- **Detached HEAD.** No branch is checked out, for example after checking out
  a tag:

  ```
  tingle update: <folder> is on a detached HEAD; check out a branch, then re-run; nothing was changed
  ```

  Check out a branch, e.g. `git -C <folder> checkout main`, then re-run.

- **No upstream.** The current branch does not track a remote branch:

  ```
  tingle update: branch '<branch>' in <folder> has no upstream; set one with 'git branch --set-upstream-to', then re-run; nothing was changed
  ```

  Set one, e.g. `git -C <folder> branch --set-upstream-to=origin/main`, then
  re-run.

- **Fetch failed.** git's own error is shown first, then:

  ```
  tingle update: could not fetch <upstream> in <folder>; nothing was changed
  ```

  Check your network connection and access to the remote, then try again.

- **Diverged branch.** The pull could not fast-forward, usually because you
  have local commits and the upstream has new ones too. git's own error is
  shown first, then:

  ```
  tingle update: git pull --ff-only failed in <folder> (has the branch diverged from <upstream>?); nothing was changed
  ```

  Reconcile the branch yourself, e.g. with `git -C <folder> pull --rebase`
  or a merge, then re-run `tingle update` (or `tingle install`).

- **Version pin.** A `<version>` argument or `TINGLE_VERSION` was given:

  ```
  tingle update: <folder> is a git checkout; version pins are not supported there. Check out a tag yourself instead, e.g. 'git -C <folder> checkout <version>'
  ```

  To run a specific release from a clone, check out its tag yourself and then
  run `tingle install`. Note that this leaves a detached HEAD, so check out a
  branch again before the next `tingle update`.

- **`--force`.**

  ```
  tingle update: --force is not supported on a git checkout (<folder>)
  ```

  Drop `--force`. To discard local edits, use git (for example
  `git -C <folder> stash`).

- **`git` missing.**

  ```
  tingle update: required tool 'git' not found on PATH
  ```

  Install git, or add it to your `PATH`.

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

# In a git checkout: see how far behind the upstream you are, then pull.
tingle update --check
tingle update
```

## What it changes and what it keeps (web installs)

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

- **An empty file list deletes nothing.** If `tingle.json` lists no shipped
  files at all (`"manifest": []`), tingle can't tell which old files are
  stale, so it removes none of them and warns:

  ```
  installer.sh: warning: '/home/you/.tingle/tingle.json' has an empty manifest; stale files from the previous version may be left behind
  ```

  The new release's files are still installed. Any file the old release
  shipped and the new one dropped stays behind; delete it by hand if you want.
- **Unsafe paths are skipped.** A file path in `tingle.json` or in the
  release's `MANIFEST` that is absolute (starts with `/`) or contains `..` is
  never hashed, replaced or deleted, so a tampered file list can't touch
  anything outside the tingle folder. Each one is reported:

  ```
  installer.sh: warning: skipping unsafe manifest path '../outside'
  ```

- **`~/.bashrc` is rewired.** As its last step the update runs
  [`tingle install`](install.md) from the updated folder, then prints:

  ```
  tingle in '/home/you/.tingle' was updated to 0.5.0.
  Already-open shells need a restart (or 'source ~/.bashrc') to pick up the new completion.
  ```

## Interrupting it

It is safe to interrupt a web-install update (Ctrl-C, a closed terminal, even a power
loss). `tingle.json` is written last, so until then it still describes the
old version. **Re-running `tingle update` finishes an interrupted update**:
either there is nothing left to do, or it redoes the update from where the
files stand.

There is one exception. The very last step, after `tingle.json` is written, is
the [`tingle install`](install.md) run that rewires `~/.bashrc`. If the update
is cut off during that step, the files and `tingle.json` are already new, so a
re-run of `tingle update` just says `tingle is already up to date (<version>)`
and does **not** rewire `~/.bashrc`. Finish it by hand:

```
<folder>/bin/tingle install
```

where `<folder>` is the tingle folder (for example `~/.tingle`).

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

The failures below apply to web installs. For a git checkout, see
[When a git checkout is not updated](#when-a-git-checkout-is-not-updated).
Every failure below exits non-zero (an update that finds nothing to do,
`tingle is already up to date (<version>)`, is not a failure and exits 0).
Unless stated otherwise, nothing in the tingle folder was changed.

- **Unknown option or extra argument:** `tingle update: unknown option
  '<option>'` or `tingle update: unexpected argument '<argument>'`, followed
  by the usage line `usage: tingle update [--check] [--force] [<version>]`.
  Only `--check`, `--force` and a single version are accepted. This applies
  to git checkouts too.
- **Missing tool:** `tingle update: required tool '<tool>' not found on PATH`,
  where `<tool>` is `curl`, `unzip` or `jq`. Install it, or add it to your
  `PATH`, and try again.

- **No network:** `could not reach ... to find the latest release (network
  failure)` or `could not download ... (network failure); nothing was
  changed`. Check your connection and try again. If only the latest-release
  lookup fails, pin a version: `tingle update X.Y.Z`.
- **Unexpected GitHub response:** `tingle update: unexpected response (HTTP
  <status>) from <api>/releases/latest; pin a version to skip the lookup, e.g.
  'tingle update X.Y.Z'`, or `tingle update: unexpected response (HTTP
  <status>) while downloading <url>; nothing was changed`. GitHub answered
  with an error other than a rate limit or "not found". Try again later, or
  pin a version to skip the latest-release lookup.
- **Latest release unreadable:** `tingle update: could not read the latest
  release's tag_name from <api>/releases/latest; pin a version to skip the
  lookup, e.g. 'tingle update X.Y.Z'`. GitHub's answer did not name a
  release. Pin a version: `tingle update X.Y.Z`.
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
- **Checksum file missing:** `tingle update: could not download the checksum
  <url>.sha256 (HTTP <status>); nothing was changed`. The release has no
  checksum file, or it could not be downloaded, so the zip can't be verified
  and is not installed. Try again later, or pick another release.
- **Bad release zip:** `tingle update: tingle-<version>.zip could not be
  unzipped; nothing was changed`, or `tingle update: tingle-<version>.zip has
  no executable install/installer.sh; nothing was changed`. The zip passed its
  checksum but is not a usable tingle release. Pick another release.
- **Broken release file list:** the release zip's `MANIFEST` (its list of
  shipped files) is missing, malformed or empty, and the update is refused:
  `installer.sh: the release tree has no MANIFEST ('<path>'); nothing was
  changed`, `installer.sh: '<path>/MANIFEST' is malformed; nothing was
  changed` or `installer.sh: '<path>/MANIFEST' is empty; nothing was changed`.
  This protects your install from a broken release that would otherwise
  delete every file. Pick another release.
- **Corrupt `tingle.json`:** `tingle update: <folder>/tingle.json is corrupt
  (it can't be parsed, or 'version', 'repo' or 'manifest' is missing);
  nothing was changed`. The file was edited or damaged. Reinstall tingle with
  the web installer into a fresh folder.
- **Not a web install:** `can't tell how tingle was installed in <folder>
  (no tingle.json and not a git checkout); nothing was changed`. Reinstall
  with the web installer to be able to use `tingle update`.
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
  [What it changes and what it keeps](#what-it-changes-and-what-it-keeps-web-installs).
- **Failure in the middle of an update:** `installer.sh: could not replace
  '<file>'; re-run the update to finish it`, or `installer.sh: could not write
  '<folder>/tingle.json'; re-run the update to finish it`. Here some files may
  already be new. `tingle.json` still describes the old version, so fix the
  cause (for example a full disk or a permissions problem) and re-run
  `tingle update` to finish; see [Interrupting it](#interrupting-it).
- **Update done, but `~/.bashrc` not rewired:** `tingle <version> was
  installed in '<folder>', but wiring ~/.bashrc failed; re-run
  '<folder>/bin/tingle install' by hand`. The new version is installed; run
  that command yourself to finish.
