# architect Plan: Image: build and publish the tingle-linux Docker image

Main plan: [plan.md](plan.md)

## Shared contracts

- Builds and publishes `shell/linux/Dockerfile` (owned by `shell`) as
  `darthjee/tingle:<tag>`.
- The smoke test must fail the job (and block publish) if
  `shell/linux/Dockerfile` doesn't produce GNU `sed` and a non-root user.
- `DOCKERHUB_DESCRIPTION.md`'s content should stay consistent with
  `product-owner`'s documented image reference/purpose.

## Implementation Steps

### Step 1 — Add `build-and-publish-linux-image` + `update-description` jobs to `.circleci/config.yml`

Add a job (e.g. `machine: true`, following the `tent` project's
`build-and-release-*` job shape) that:

1. Checks out the repo.
2. Builds `shell/linux/Dockerfile`: `docker build -t
   darthjee/tingle:$CIRCLE_TAG -f shell/linux/Dockerfile .`.
3. Smoke-tests the built image: run `sed --version` inside it and assert
   GNU sed in the output; assert the container's effective user is
   non-root (e.g. `docker run --rm <image> id -u` is not `0`).
4. Only if the smoke test passes: log in via `echo "$DOCKER_HUB_PASSWORD" |
   docker login -u "$DOCKER_HUB_USERNAME" --password-stdin`, then `docker
   push darthjee/tingle:$CIRCLE_TAG`.

Add this job to the `workflows` section filtered to tags only (`filters: {
tags: { only: /v.*/ }, branches: { ignore: /.*/ } }`), so it never runs on
ordinary branch/PR builds.

Add a second, lightweight `update-description` job that `requires:
[build-and-publish-linux-image]` and, once the image is published, pushes
`DOCKERHUB_DESCRIPTION.md`'s content as the Docker Hub repo description for
`darthjee/tingle` — mirroring the `tent` project's `update-description` job
(reuse an existing Docker Hub description-push script/image if one is
available; otherwise call the Docker Hub API directly with `curl`). Same
tags-only filter as the publish job.

### Step 2 — Add `DOCKERHUB_DESCRIPTION.md`

Root-level file describing the `darthjee/tingle` image's purpose (a
GNU/Linux tool container backing `tingle linux`) and basic usage, consumed
by Step 1's `update-description` job.

## Files to Change

- `.circleci/config.yml` — add the `build-and-publish-linux-image` and
  `update-description` jobs, wired into the tags-filtered workflow.
- `DOCKERHUB_DESCRIPTION.md` — new, root-level.

## Notes

- `DOCKER_HUB_USERNAME` / `DOCKER_HUB_PASSWORD` must be set as
  project-level environment variables in CircleCI's project settings — this
  is a manual, out-of-repo step that cannot be automated from this PR; flag
  it as a prerequisite for the new jobs to actually succeed on the next tag
  push.
- No local equivalent for the new CI jobs themselves (they only run on a
  tag push) — verify locally via `docker build -f shell/linux/Dockerfile .`
  plus the same smoke commands (`sed --version`, `id -u`) before pushing a
  tag.
