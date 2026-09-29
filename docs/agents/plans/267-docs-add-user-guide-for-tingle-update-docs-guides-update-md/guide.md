# Plan: docs: add user guide for tingle update (docs/guides/update.md)

Issue: [267-docs-add-user-guide-for-tingle-update-docs-guides-update-md.md](../../issues/267-docs-add-user-guide-for-tingle-update-docs-guides-update-md.md)

## Overview
Write `docs/guides/update.md` describing `tingle update` as shipped in #266,
and wire it into the existing guide links. Documentation only.

## Context
`tingle update --help` (`long_help` in `commands/shell.json`) already says
"See docs/guides/update.md for more details", but the file does not exist.
The installer's "`tingle.json` already exists" message already points at
`tingle update` (done in #265), so `install/installer.sh` is out of scope.

Sources of truth for the guide's content, in order:
1. `long_help` for `update` in `commands/shell.json` (user-facing wording).
2. The header comment of `shell/update/executor.sh` (flow, errors, exit codes).
3. The update-mode header of `install/installer.sh` (lock, local-edit
   detection, pre-0.4.0 installs without hashes, recovery after interruption,
   files the user added being kept).

## Implementation Steps

### Step 1 — Write `docs/guides/update.md`
Follow the shape of the existing guides (`install.md`, `uninstall.md`):
`# \`tingle update\`` title, one-line summary, then sections such as:
- **What it does** — updates the web install (with `tingle.json`, made by the
  `curl | bash` installer from the README's Installation section) that the
  running `tingle` belongs to; names the folder in its output. A git checkout
  is refused with a message to use `git pull` (non-zero exit).
- **Usage** — `tingle update [--check] [--force] [<version>]`, with examples:
  - no version → latest stable release (pre-releases/drafts skipped);
    "tingle is already up to date (<version>)" when nothing to do;
  - `tingle update <version>` / `TINGLE_VERSION`: X.Y.Z or X.Y.Z-<suffix>, no
    `v` prefix, 0.4.0 or later, downgrades and pre-releases allowed, the
    argument wins over the env var;
  - `--check` dry run (installed → target, locally edited shipped files);
  - `--force` overwrites locally edited shipped files.
- **Confirmation** — y/N prompt; `TINGLE_ASSUME_YES` (any value) skips it and
  is required without a terminal.
- **What it changes / keeps** — the release zip is verified against its
  SHA-256 checksum before anything is replaced; files the user added are kept;
  locally edited shipped files abort the update unless `--force`; installs
  from before 0.4.0 record no hashes, so edits can't be detected there.
- **Interrupting it** — safe to interrupt; re-running finishes an interrupted
  update (a stale lock from a dead process is cleared).
- **After updating** — already-open shells need a restart or
  `source ~/.bashrc` to pick up the new completion.
- **Troubleshooting** — what each common error means and what to do: no
  network / GitHub rate limit, release not found, invalid or pre-0.4.0 pin,
  checksum mismatch, corrupt `tingle.json`, folder not writable, another
  update in progress, no terminal without `TINGLE_ASSUME_YES`, git checkout.
  Use the exact messages from the scripts where they exist (e.g.
  "release <version> not found in <repo>",
  "tingle update can only install 0.4.0 or later").

Do **not** document the test-only `TINGLE_RELEASE_API_URL` /
`TINGLE_RELEASE_BASE_URL`, nor the installer-internal
`TINGLE_UPDATE_TARGET` / `TINGLE_UPDATE_FORCE` / `TINGLE_UPDATE_CLEANUP`.

### Step 2 — Link the guide
- `docs/guides/README.md`: add an `update` entry to the Guides list (after
  `uninstall`), using the `short_help` wording.
- `docs/guides/install.md`: add a short "Updating" section (next to
  "Uninstalling") saying that to upgrade a web install later, see the
  [`update` guide](update.md).
- `README.md` (root): turn the `update` cell of the commands table into a
  link to `docs/guides/update.md`, like the other rows.

## Files to Change
- `docs/guides/update.md` — new guide.
- `docs/guides/README.md` — index entry.
- `docs/guides/install.md` — cross-link to the update guide.
- `README.md` — link the `update` row of the commands table.

## Notes
- Verify statements against the scripts rather than inventing behavior; run
  `bin/tingle --help update` to compare wording.
- No CI job lints Markdown; just check that relative links resolve.
