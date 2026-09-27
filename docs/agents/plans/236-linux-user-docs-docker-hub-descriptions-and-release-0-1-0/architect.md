# Architect Plan: linux: user docs, Docker Hub descriptions and release 0.1.0

Main plan: [plan.md](plan.md)

## Shared contracts

- Use the **grouped tool list** from [plan.md](plan.md#shared-contracts)
  verbatim (seven groups, same order and names).
- Short description string (exact, 93 characters):
  `GNU/Linux toolbox (GNU utils, git, jq, kubectl, aws CLI, ...) behind the tingle linux command`
- Version `0.1.0`; README "Next Release" `0.1.1`.
- Guide anchor you may link to:
  `https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md#whats-inside-the-shell`

## Implementation Steps

### Step 1 — Refresh the Docker Hub descriptions
- `DOCKERHUB_SHORT_DESCRIPTION.txt`: replace the content with the exact short
  description above (single line). `scripts/release_image.sh update-description`
  rejects anything over 100 characters after trimming.
- `DOCKERHUB_DESCRIPTION.md`:
  - Intro: describe it as the GNU/Linux toolbox image behind `tingle linux`
    (no longer "GNU toolbox" with a baseline only).
  - "What it contains": replace the 7-package baseline list with the grouped
    tool list, keeping "Built on `ubuntu:24.04`".
  - Fix statements parts 1–3 made stale: "There is no `CMD` or `ENTRYPOINT`"
    is wrong now. Say the image has an entrypoint
    (`/usr/local/bin/tingle-entrypoint`) that wraps every command and gives an
    unknown uid (such as the host uid `tingle linux` passes) a usable identity,
    and that with no command it runs `bash`. Keep the non-root `tingle`
    (uid 1000) note.
  - Optionally one sentence that `tingle linux shell` brings in host
    git/ssh/kube/aws config (opt out with `--isolated`), linking to the guide
    for details and security notes. Don't duplicate the guide's full
    host-integration section.
  - Keep every link an absolute `https://github.com/darthjee/tingle/...` URL
    (Docker Hub doesn't resolve relative links). Keep the Tags and Links
    sections.

### Step 2 — Bump the release version to 0.1.0
Run `scripts/bump-version.sh 0.1.0` from the repo root (it uses BSD
`sed -i ''`, so run it on macOS or adapt locally without committing changes to
the script). Expected diff, same shape as commit 466da55 (#145):
- `README.md`: Current Version `0.1.0`
  (`releases/tag/0.1.0`), Next Release `0.1.1` (`compare/0.1.0...main`);
- `install/bootstrap.sh`: `VERSION="${TINGLE_VERSION:-0.1.0}"`;
- `shell/linux/VERSION`: `0.1.0` (from `0.0.3`).

Don't create or push the git tag — that is the manual release step after merge.

## Files to Change
- `DOCKERHUB_SHORT_DESCRIPTION.txt` — new one-line summary
- `DOCKERHUB_DESCRIPTION.md` — grouped tool list, entrypoint/CMD correction, host-integration pointer
- `README.md` — version lines (via `bump-version.sh`)
- `install/bootstrap.sh` — pinned `TINGLE_VERSION` default (via `bump-version.sh`)
- `shell/linux/VERSION` — `0.1.0` (via `bump-version.sh`)

## CI Checks
- `pytest` (CI job: `tests`) — run it after the bump in case any test reads
  `shell/linux/VERSION` or `install/bootstrap.sh`.
- Markdown is checked by Codacy (markdownlint): no emphasis used as a heading,
  no raw HTML such as `<kbd>`.

## Notes
- Verify the short description length before committing:
  `printf '%s' "$(cat DOCKERHUB_SHORT_DESCRIPTION.txt)" | wc -c` → `93`.
