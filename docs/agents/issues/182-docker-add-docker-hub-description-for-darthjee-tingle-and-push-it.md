# Issue: Docker: set Docker Hub short description, refresh DOCKERHUB_DESCRIPTION.md and harden update-description

## Description
The `darthjee/tingle` Docker Hub repository (the GNU toolbox image behind
`tingle linux`) looks undescribed. The original report said
`DOCKERHUB_DESCRIPTION.md` was never added, but it has existed at the repo
root since #35, and the `update-description` CircleCI job has already pushed
it: the Docker Hub API returns it as `full_description`.

What is actually missing or out of date:
- The **short description** (the one-line `description` field shown in
  Docker Hub search results and on the repo card) is empty.
  `scripts/release_image.sh update-description` only sends
  `full_description`.
- `DOCKERHUB_DESCRIPTION.md` is stale or incomplete. It says tags are
  "published manually" (CI publishes them now). It does not mention that the
  image has no CMD/ENTRYPOINT. It does not show `tingle linux` as the main
  way to use the image, and it does not link to the `tingle linux` user
  guide (`docs/guides/linux.md`, added in #176).
- `cmd_update_description` uses `curl -s` without `-f`, so an API error on
  the PATCH (for example a 4xx) still exits 0.

Came up while refining #176 (the `tingle linux` user guide).

## Problem
People who find the image on Docker Hub see no summary line. The long
description does not point them to `tingle linux` or its guide, and it
partly describes an old release process. A failed description push can go
unnoticed in CI.

## Expected Behavior
- The Docker Hub short description is set to a one-line summary (Docker Hub
  allows at most 100 characters). It lives in a new repo-root file,
  `DOCKERHUB_SHORT_DESCRIPTION.txt`, next to `DOCKERHUB_DESCRIPTION.md`, so
  it can be edited without touching the script.
- `DOCKERHUB_DESCRIPTION.md` is refreshed and covers:
  - what the image is: the GNU toolbox image behind `tingle linux`
  - what it contains: coreutils, findutils, grep, sed, gawk, tar and
    diffutils on `ubuntu:24.04`
  - that it runs as a non-root user (uid 1000) and has no CMD/ENTRYPOINT
  - how to use it: through `tingle linux` (preferred), or directly with
    `docker run --rm -v "$PWD:$PWD" -w "$PWD" darthjee/tingle:<tag> <cmd>`
  - how tags work, with the stale "published manually" wording fixed
  - links to the GitHub repo and to the `tingle linux` guide
    (`docs/guides/linux.md`)
- `scripts/release_image.sh update-description` reads both files and sends
  `description` and `full_description` in the same PATCH. It fails loudly:
  it checks that both files exist, rejects a short description longer than
  100 characters, and uses `curl -f` (or checks the HTTP status) on both
  the login and PATCH calls.
- The updated descriptions reach Docker Hub through the existing
  `update-description` CircleCI job on the next release tag. This issue
  does not need a manual push.
