# Issue: docs: add user guide for tingle update (docs/guides/update.md)

## Description
Document the `tingle update` command for end users, following the
per-command guide precedent (#175, #177, #178).

Sub-issue 4 of 4 of #263. Its dependency, sub-issue 3 (#266, the
`tingle update` command), is merged, so the guide documents that behavior as
shipped. `tingle update --help` already points at `docs/guides/update.md`,
which does not exist yet.

## Problem
`tingle update`'s long help refers users to `docs/guides/update.md`, but
that guide is missing and the guides index does not list the command. Users
have no end-user reference for how updates, pins, local edits and failures
behave.

## Expected Behavior
- **New `docs/guides/update.md`** covering:
  - what it updates: the web install (one with `tingle.json`, made with the
    `curl | bash` installer) that the running `tingle` belongs to, named in
    its output; a git checkout is refused and must use `git pull`;
  - usage: `tingle update` (latest stable release; pre-releases and drafts
    skipped; "already up to date" when nothing to do),
    `tingle update <version>` / `TINGLE_VERSION` (X.Y.Z or X.Y.Z-suffix, no
    `v`, 0.4.0 or later, downgrades and pre-releases allowed, argument wins
    over the env var), `--check`, `--force`, and the y/N confirmation with
    `TINGLE_ASSUME_YES` (required without a terminal);
  - that the release zip is verified against its SHA-256 checksum before
    anything is replaced;
  - that files the user added to the install folder are kept, while locally
    edited shipped files make it abort unless `--force` is given (which
    overwrites them), and that installs from before 0.4.0 record no hashes
    and so can't detect such edits;
  - that it is safe to interrupt: re-running finishes an interrupted update;
  - that already-open shells need a restart or `source ~/.bashrc` for the
    new completion;
  - what the common errors mean: no network or rate limit, release not
    found, invalid or pre-0.4.0 pin, checksum mismatch, corrupt
    `tingle.json`, folder not writable, another update in progress (lock),
    no terminal without `TINGLE_ASSUME_YES`.
- **The test-only env vars** (`TINGLE_RELEASE_API_URL`,
  `TINGLE_RELEASE_BASE_URL`) and the installer's internal ones
  (`TINGLE_UPDATE_TARGET`, `TINGLE_UPDATE_FORCE`, `TINGLE_UPDATE_CLEANUP`)
  are **not** documented in the guide.
- **`docs/guides/README.md`:** link the new guide from the index.
- **`docs/guides/install.md`:** cross-link it ("to upgrade later, see
  update.md").

## Solution
- guide agent: write `docs/guides/update.md`, and update `README.md` and
  `install.md`. Keep the guide consistent with `long_help` in
  `commands/shell.json`, the header comment of `shell/update/executor.sh`,
  and the update-mode header of `install/installer.sh`.
- Out of scope: the installer's "`tingle.json` already exists" message
  already tells the user to run `tingle update` (done in #265).

## Testing
- The links resolve, and the guide matches `tingle update --help` and the
  actual behavior.

## Responsible agents
guide (`docs/guides/`).
