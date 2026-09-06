# Shell Plan: Install: curl | bash bootstrap and in-zip installer

Main plan: [plan.md](plan.md)

## Shared contracts

None — this is the sole agent involved. `install/` is a new top-level tree
(outside `shell/`), but stays plain bash and is owned by `shell` per the
issue's explicit ownership decision (extending `shell`'s scope rather than
assigning a new specialist or `architect`).

## Implementation Steps

### Step 1 — `install/bootstrap.sh` (blindly-run curl | bash entry point)
Small, auditable script — this is the only piece ever run via
`curl | bash`, so keep its surface minimal (no `set -x`, no unnecessary
logic):
- `REPO="${TINGLE_REPO:-darthjee/tingle}"`,
  `VERSION="${TINGLE_VERSION:-<pin>}"` — the pinned literal mirrors whatever
  `shell/linux/VERSION` holds at implementation time. **Check
  `shell/linux/VERSION` and the tag-convention outcome of #49 (blocking #46)
  before picking the literal** — it must be a real, currently-published tag,
  not necessarily `v0.0.1` by the time this is implemented.
- Prereq check: verify `curl`, `unzip`, `bash` are present; fail with a clear
  message naming the missing tool(s) if not.
- Build `URL=https://github.com/$REPO/releases/download/$VERSION/tingle-$VERSION.zip`,
  print it, then confirm on `/dev/tty` (`y/N`) — skipped entirely when
  `TINGLE_ASSUME_YES` is set (read as a one-off env prefix, e.g.
  `TINGLE_ASSUME_YES=1 curl ... | bash`, not something the user is told to
  `export`). If `/dev/tty` is unavailable (CI/container) and
  `TINGLE_ASSUME_YES` is unset, fail clearly rather than hang.
- `mktemp -d` for a disposable work dir (`WORK`); trap cleanup on any failure
  path (partial download, failed unzip) so nothing is left behind and nothing
  is copied to a real target from this script.
- `curl -f -fsSL -o "$WORK/tingle.zip" "$URL"` — `-f` so a bad
  tag/repo/network failure exits non-zero with the URL visible, not a
  silently-empty file.
- `unzip -q "$WORK/tingle.zip" -d "$WORK"`.
- `exec "$WORK/install/installer.sh"` — replaces this process, so
  `installer.sh` inherits the same `/dev/tty`-based prompting approach and
  the same work dir path if it needs it.
- Header comment documents `TINGLE_REPO`, `TINGLE_VERSION`,
  `TINGLE_ASSUME_YES` (per the repo's per-script header-comment convention).

### Step 2 — `install/installer.sh` (shipped inside the zip)
Runs unpacked, already on disk (not piped), versioned with the release it
ships in:
- Prereq check: verify `curl`, `unzip`, `bash` again (defensive — this file
  can also be run standalone against an already-downloaded zip); additionally
  **warn** (do not fail) if `jq` (needed by `bin/tingle`) or `docker` (needed
  by `tingle linux`) is missing.
- Prompt for a target directory on `/dev/tty` (stdin is the piped script),
  defaulting to `~/.tingle`. If `/dev/tty` is unavailable, fall back silently
  to the default (no assume-yes flag needed here — this prompt has a safe
  default, unlike bootstrap's destructive-ish confirm).
- Expand/normalize the entered path (`~`, relative paths) before use.
- **Refuse** if `<target>/tingle.json` already exists: print a message
  pointing at a future `update` flow, exit non-zero, touch nothing else.
- Copy the unpacked tree (the script's own directory's parent — i.e. the
  unzipped root containing `bin/`, `shell/`, `completions/`, etc.) into
  `<target>`.
- Write `<target>/tingle.json`:
  ```json
  { "version": "<tag>", "repo": "<repo>", "manifest": [ "...lines of the embedded MANIFEST..." ] }
  ```
  `<tag>` and `<repo>` come from `VERSION`/`REPO` (inherited env from
  bootstrap, or sensible fallback if run standalone); `manifest` is the
  embedded `MANIFEST` file's lines (produced by #46 — read it from the
  unpacked tree, one JSON string per line).
- Run `"<target>/bin/tingle" install` as the final step — this appends the
  `~/.bashrc` marker block via the existing, **unchanged**
  `shell/install/executor.sh` (`MARKER_START="# >>> tingle >>>"` /
  `MARKER_END="# <<< tingle <<<"`, already idempotent via
  `grep -qF "$MARKER_START"`) — do not reimplement any `.bashrc` editing
  here. Note the marker block will now point at `<target>` (e.g. `~/.tingle`)
  rather than a git checkout, since `executor.sh` derives its path from its
  own script location (`shell/install/executor.sh:20`,
  `TINGLE_FOLDER="$(cd "$(dirname "$0")/../.." && pwd)"`) — this works
  unchanged once the tree is copied into `<target>`.
- Print the same "run `source ~/.bashrc` or restart your shell" hint
  `executor.sh` already prints (it prints its own, so nothing extra is needed
  here beyond letting `tingle install`'s own output surface).

## Files to Change
- `install/bootstrap.sh` — new; curl-piped entry point (Step 1).
- `install/installer.sh` — new; in-zip installer, `tingle.json` writer, calls
  `tingle install` (Step 2).

## Notes
- Depends on #46 (needs `tingle-<tag>.zip` as a Release asset, the `MANIFEST`
  format, and the `EXCLUDES` set — `install/` itself must be inside the zip,
  confirmed in the issue's Solution section). Confirm #46 has actually
  merged, and pin `VERSION`/read the tag-convention format from whatever #49
  landed as, before writing the literal in Step 1.
- Blocks sub-issue #48 (README documents this script's behavior and flags) —
  no action needed here, just don't expect README updates in this PR.
- No CI job currently lints or tests `shell/` (`.circleci/config.yml` only
  runs `lint`/`tests` against `python/`, and image-release jobs) — no
  `## CI Checks` section applies. `shellcheck` is contributing.md's suggested
  local check for `shell/`; run it manually before opening the PR since CI
  won't catch shell issues.
- Manual verification (from the issue, not CI-automatable): from a machine
  without the repo, run the real one-liner against a real published tag;
  confirm `~/.tingle` is populated, `tingle.json` is correct, `~/.bashrc` has
  the marker block exactly once, `tingle help` works in a new shell, and
  re-running the one-liner is refused because `tingle.json` exists.
- Edge cases to handle explicitly (from the issue): bad/nonexistent
  `TINGLE_VERSION` or `TINGLE_REPO` → `curl -f` fails, surfaced URL, non-zero
  exit, no partial install; re-running over an existing install → refused by
  the `tingle.json` guard; relative/`~` target paths → normalized; existing
  `~/.bashrc` marker block (e.g. from a prior cloned install) → `tingle
  install` already no-ops safely; non-interactive/no `/dev/tty` → covered per
  script above; partial download/interrupted unzip → disposable work dir,
  nothing copied until unzip succeeds.
