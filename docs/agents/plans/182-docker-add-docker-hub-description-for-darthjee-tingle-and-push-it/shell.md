# Shell Plan: Docker: set Docker Hub short description, refresh DOCKERHUB_DESCRIPTION.md and harden update-description

Main plan: [plan.md](plan.md)

## Shared contracts

- Produce `DOCKERHUB_SHORT_DESCRIPTION.txt` at repo root: a single line
  whose trimmed content is 1–100 characters.
- Keep `DOCKERHUB_DESCRIPTION.md` at repo root (Markdown).
- `update-description` sends
  `PATCH https://hub.docker.com/v2/repositories/darthjee/tingle/` with body
  `{"description": <short>, "full_description": <full>}`.
- `update-description` exits non-zero when either file is missing, when the
  short description is empty or longer than 100 characters, or when the
  login or PATCH HTTP call fails.

## Implementation Steps

### Step 1 — Write the description files
Create `DOCKERHUB_SHORT_DESCRIPTION.txt` with a single-line summary of 100
characters or less, for example: `GNU toolbox image (coreutils, sed, grep,
gawk, ...) behind the tingle linux command`. Count the characters before
committing.

Rewrite `DOCKERHUB_DESCRIPTION.md` so it covers:
- what the image is: the GNU toolbox image behind `tingle linux`
- what it contains: coreutils, findutils, grep, sed, gawk, tar and diffutils
  on `ubuntu:24.04`, matching `shell/linux/Dockerfile`
- that it runs as the non-root user `tingle` (uid 1000) and has no
  CMD/ENTRYPOINT, so every run supplies its own command
- how to use it:
  - through `tingle linux` (preferred)
  - directly with
    `docker run --rm -v "$PWD:$PWD" -w "$PWD" darthjee/tingle:<tag> <cmd> [args...]`
- tags:
  - plain semver, same string as the `X.Y.Z` git tag
  - built and published by CircleCI when that git tag is pushed (this
    replaces the stale "published manually" wording)
  - the current tag is pinned in `shell/linux/VERSION`
- links, as absolute GitHub URLs because Docker Hub cannot resolve relative
  links:
  - the repo: https://github.com/darthjee/tingle
  - the guide: https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md
  - the Dockerfile

### Step 2 — Harden and extend `cmd_update_description`
In `scripts/release_image.sh`:
- Add constants for both file names, next to `VERSION_FILE` and
  `IMAGE_NAME`.
- Before any network call:
  - check that both files exist, and print a clear error to stderr if not
  - read the short description with surrounding whitespace trimmed
  - reject it if it is empty or longer than 100 characters
- Use `curl -fsS` on the login call so HTTP errors fail the command. Keep
  the `python3` token extraction, which already fails on a missing `token`.
- Build the JSON body with `python3`/`json.dumps` for both fields, so the
  content is escaped correctly. Send it with `curl -fsS -X PATCH`, and
  redirect the response body to `/dev/null` so the job log stays small.
- Print a short success line at the end, for example
  `Updated Docker Hub description for darthjee/tingle`.
- Update the header comment to mention both description files.

Note that `set -euo pipefail` is already on. Declare `local` separately from
the `$(...)` assignments, as the current code does, so failures inside
command substitution still abort the script.

## Files to Change
- `DOCKERHUB_SHORT_DESCRIPTION.txt`: new file with the one-line Docker Hub
  summary
- `DOCKERHUB_DESCRIPTION.md`: refreshed full description
- `scripts/release_image.sh`: read both files, validate them, send both
  fields, and fail on HTTP errors

## Notes
- There is no local test for the real API call, since it needs Docker Hub
  credentials. Check the change by running the script in a shell with a
  missing file or an over-long summary and confirming it exits non-zero
  before any `curl` call. Also run `bash -n scripts/release_image.sh`.
- Do not change `.circleci/config.yml`: the existing `update-description`
  job already runs `scripts/release_image.sh update-description` on
  release tags.
