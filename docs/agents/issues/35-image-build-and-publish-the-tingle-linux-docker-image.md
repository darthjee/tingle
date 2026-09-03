# Issue: Image: build and publish the tingle-linux Docker image

## Description
Builds and publishes the `tingle-linux` Docker image that `tingle linux`
(parent issue #34) depends on to run GNU/Linux tools inside a container,
independent of macOS's BSD userland. This is the first of four sequential
sub-issues splitting #34, and it is standalone: it unblocks the rest, since
every later sub-issue needs a real, published image reference to configure
and test against end-to-end.

## Problem
`tingle linux` needs a container image with the right GNU tools, non-root
user, and volume-mount semantics before any subcommand (`shell`, `sed`, ...)
can be built against it. That image doesn't exist yet, and nothing currently
builds or publishes it.

## Expected Behavior
- A `Dockerfile` (under `shell/linux/`, following the stack decision in #34)
  builds a non-root, `ubuntu`-based image with a baseline GNU toolbox.
- Pushing a `v*` git tag triggers a CircleCI job that builds the image,
  smoke-tests it, and — only if the smoke test passes — logs in and
  publishes it to Docker Hub as `darthjee/tingle:<tag>`.
- The image's Docker Hub repo description is kept up to date automatically
  as part of the same publish job.
- The resulting image name/tag reference is documented somewhere
  discoverable (e.g. `docs/agents/`) so sub-issue 2 (command skeleton) can
  configure its `docker run` wrapper against it.

## Solution

### Scope
- A `Dockerfile` based on `ubuntu`, non-root user, no unnecessary layers,
  following the pattern of the existing `python/Dockerfile`.
- A CircleCI job (in the existing `.circleci/config.yml`) that builds,
  smoke-tests, and publishes this image to Docker Hub.
- Document the resulting image name/tag reference for sub-issue 2 to
  consume.

### Image name & tag strategy
- Docker Hub repo: `darthjee/tingle` (single shared image repo across
  tingle's Docker-based tooling, distinguished by tag rather than name).
- Tag: plain semver, e.g. `v1.0.0`. This assumes `darthjee/tingle` stays the
  only image published under this repo; if a second distinct image is ever
  needed there, tags will need a distinguishing prefix at that point.
- Trigger: publish on manual git tag push matching `v*` (no automatic
  `latest` movement, no auto-bump on merge to `main`). Pushing a tag is a
  deliberate, manual release action.

### CI credentials & Docker Hub description
Following the pattern used in the `tent` project's `.circleci/config.yml`
(`build-and-release-*` and `update-description` jobs):
- Credentials: project-level CircleCI env vars `DOCKER_HUB_USERNAME` /
  `DOCKER_HUB_PASSWORD`, set in CircleCI project settings (not a shared
  context — this is the only repo currently publishing this image). Login
  step: `echo "$DOCKER_HUB_PASSWORD" | docker login -u
  "$DOCKER_HUB_USERNAME" --password-stdin`.
- The publish job is filtered to tags only (`filters: tags: only: /v.*/`,
  branches ignored) — it does not run on ordinary branch/PR builds.
- Add a `DOCKERHUB_DESCRIPTION.md` file documenting the image, and an
  `update-description` CircleCI job (requiring the build/publish job) that
  pushes it to Docker Hub's repo description for `darthjee/tingle`,
  mirroring `tent`'s `update-description` job.

### GNU tools scope
The parent issue (#34)'s initial subcommand set is only `shell` (bash) and
`sed`, but the image pre-installs a broader baseline GNU toolbox upfront
rather than growing package-by-package with each new subcommand:
- `coreutils`, `findutils`, `grep`, `sed`, `gawk`, `tar`, `diffutils` — the
  classic GNU text/file toolbox, on top of Ubuntu's base packages. This
  covers the most likely candidates for future subcommands (`tingle linux
  find`, `tingle linux awk`, etc.) without pulling in a full dev toolbox
  (no `build-essential`, `curl`, `git`, etc. — those are out of scope unless
  a future subcommand specifically needs them).

### Testing strategy
The CircleCI publish job runs a smoke test against the freshly built image
*before* the Docker Hub login/publish step, so a broken image never gets
published:
- Build the image locally in the job.
- Run quick checks inside it, e.g. `sed --version` (confirms GNU sed, not
  BSD), confirm the non-root user is set up correctly, and confirm the
  cwd-mount pattern (`-v $(pwd):$(pwd) -w $(pwd)`) works as expected.
- If the smoke test fails, the job fails and the login/publish steps never
  run.

### Out of scope
- The `tingle linux` command itself (dispatcher, subcommands) — tracked in
  the other sub-issues of #34.

### Dependencies
None — this is the first sub-issue of #34 and unblocks the rest.

## Benefits
- Unblocks sub-issues 2-4 of #34 (command skeleton, `shell`, `sed`), all of
  which need a real published image to configure/test against.
- Gives `tingle linux` (and any future GNU-tool subcommand) reliable GNU
  behavior independent of macOS's BSD userland.
- Non-root container execution keeps host-file ownership correct out of the
  box, with no lingering containers (ephemeral `docker run --rm`).
