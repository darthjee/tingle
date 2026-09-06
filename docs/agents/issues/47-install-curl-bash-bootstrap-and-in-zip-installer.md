## Description
Second of three sub-issues splitting #45 (`Add tingle web install (curl | bash)`).
Adds the two scripts that turn a published `tingle-<tag>.zip` (sub-issue 1) into
an installed, shell-wired tingle: a small auditable `install/bootstrap.sh`
fetched fresh from `main` and piped to `bash`, and an `install/installer.sh` that
ships **inside** the zip. Mirrors arcanum's `bootstrap.sh` + `installer.sh` split
by trust boundary.

## Problem
Once sub-issue 1 publishes `tingle-<tag>.zip` as a GitHub Release asset, nothing
downloads or installs it. `tingle install` (`shell/install/executor.sh`) only
wires an **already-present** checkout into `~/.bashrc` — it has no download step
and hardcodes the checkout path. A user without the repo still cannot get
`tingle`.

## Expected Behavior
- `curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash`
  downloads the pinned release zip, unpacks it, and installs tingle to
  `~/.tingle`, leaving `tingle` available in new shells.
- `install/bootstrap.sh` (run blindly via `curl | bash`):
  - `REPO="${TINGLE_REPO:-darthjee/tingle}"`,
    `VERSION="${TINGLE_VERSION:-<DEFAULT_VERSION>}"` (a literal pinned in the
    file, bumped per release alongside `shell/linux/VERSION`). Initial value
    mirrors whatever `shell/linux/VERSION` holds at implementation time
    (currently `v0.0.1`) — note the tag convention itself (`vX.Y.Z` vs
    `X.Y.Z`) is being settled by #49, which #46 already depends on; this
    literal must match whatever convention has landed by the time #47 is
    implemented.
  - Builds `URL=https://github.com/$REPO/releases/download/$VERSION/tingle-$VERSION.zip`,
    prints it, and asks `y/N` on `/dev/tty` — **skipped** when `TINGLE_ASSUME_YES`
    is set (a one-off prefix, not something to `export`).
  - `curl -fsSL -o "$WORK/tingle.zip" "$URL"`; `unzip -q` into `$WORK`;
    `exec "$WORK/install/installer.sh"`.
  - Uses a `mktemp -d` work dir and cleans it up on failure; no `set -x`; minimal
    surface, since this is the only blindly-executed piece.
- `install/installer.sh` (shipped inside the zip, versioned with the release):
  - Prompts for a target directory (default `~/.tingle`), reading from `/dev/tty`
    since stdin is the piped script.
  - **Refuses** if `<target>/tingle.json` already exists — prints a message
    pointing at a future `update` flow, exits non-zero, touches nothing.
  - Copies the unpacked tree into `<target>`.
  - Writes `<target>/tingle.json`: `{ "version": "<tag>", "repo": "<repo>",
    "manifest": [ ...lines of the embedded MANIFEST... ] }`.
  - Runs `"<target>/bin/tingle" install` as the final step to append the
    `~/.bashrc` marker block — `tingle install` itself is **unchanged**.
  - Prints the same "run `source ~/.bashrc` or restart your shell" hint the
    existing installer prints.
- Prereq check: both scripts verify `curl`, `unzip`, `bash` are present and fail
  with a clear message; `installer.sh` additionally **warns** (does not fail) if
  `jq` (needed by `bin/tingle`) or `docker` (needed by `tingle linux`) is missing.
- Manual verification: from a machine without the repo, run the one-liner against
  a real published tag; confirm `~/.tingle` is populated, `tingle.json` is
  correct, `~/.bashrc` has the marker block once, `tingle help` works in a new
  shell, and re-running the one-liner is refused because `tingle.json` exists.

### Edge cases
- **`TINGLE_VERSION` pins an old/nonexistent tag** — `curl -f` fails on the
  download; surface the URL and a non-zero exit, no partial install.
- **`TINGLE_REPO` points at a fork without that release** — same failure path.
- **Re-running the one-liner over an existing install** — refused by the
  `tingle.json` guard; existing install untouched.
- **Target dir given as a relative path or with `~`** — expand/normalize before
  use.
- **`~/.bashrc` already has the tingle marker block** (e.g. from a prior cloned
  install) — `tingle install` is already idempotent; installer must not
  double-append. Note the marker block will now point at `~/.tingle` rather than
  a clone.
- **Non-interactive / no `/dev/tty`** (CI, container) — `TINGLE_ASSUME_YES`
  covers the confirm prompt; the target-dir prompt should fall back to the
  default when `/dev/tty` is unavailable.
- **Partial download / interrupted unzip** — work dir is disposable; nothing is
  copied to the target until the unzip succeeds.

## Solution
- New top-level `install/` directory (keeps the web-install bootstrap separate
  from `shell/install/`, which stays the `tingle install` command
  implementation):
  - `install/bootstrap.sh` — override resolution, confirm prompt, download,
    unzip, `exec` installer. Header comment documents `TINGLE_REPO` /
    `TINGLE_VERSION` / `TINGLE_ASSUME_YES`.
  - `install/installer.sh` — target-dir prompt, `tingle.json` guard, copy,
    `tingle.json` write (from the embedded `MANIFEST`), then
    `exec "<target>/bin/tingle" install`.
- `install/bootstrap.sh` is what sub-issue 1's `EXCLUDES` must **not** exclude in
  reverse: `install/` (at least `installer.sh`) must be **inside** the zip;
  `bootstrap.sh` is fetched from `main` directly, so whether it is also packaged
  is a don't-care (simplest: package the whole `install/` dir).
- `tingle.json` schema is defined here and is the shared contract for a future
  `update` flow.
- Reuse the existing marker-block constants / behavior from
  `shell/install/executor.sh` rather than reimplementing `.bashrc` editing.
- `bash`, `snake_case` filenames, `set -euo pipefail`, per-script header
  comment — per `docs/agents/contributing.md` and `.claude/agents/shell.md`.

### Scope
- `install/bootstrap.sh`, `install/installer.sh`.
- `tingle.json` schema/writer.
- Prereq/dependency checks and the `/dev/tty` prompting.

### Out of scope
- Building/publishing the zip and the `MANIFEST` — sub-issue 1.
- README docs — sub-issue 3.
- Any change to `tingle install` (`shell/install/`) — it is called as-is.
- An `update` / re-install flow (the `tingle.json` guard just points at it).
- zsh/fish support.

### Dependencies
- **Depends on sub-issue 1** — needs `tingle-<tag>.zip` to exist as a Release
  asset, the `MANIFEST` format, and the `EXCLUDES` set (so `install/` is
  packaged). Blocked until #1 merges.
- Blocks sub-issue 3 (README documents this script's behavior and flags).

### Responsible agent(s)
- `shell` — both scripts live under a new top-level `install/` tree; this
  extends `shell`'s scope beyond `shell/` proper (still plain bash scripts,
  same conventions), rather than assigning a new specialist or `architect`.

## Benefits
- Delivers the actual "download a zip and run the install" behavior #45 is about.
- The trust-boundary split (tiny bootstrap from `main`, full installer versioned
  in the zip) keeps the blindly-run surface auditable.
- `tingle.json` + reuse of `tingle install` means no duplicated `.bashrc` logic
  and a clean hook for a later `update` flow.
