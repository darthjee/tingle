# Plan: Image: build and publish the tingle-linux Docker image

Issue: [35-image-build-and-publish-the-tingle-linux-docker-image.md](../issues/35-image-build-and-publish-the-tingle-linux-docker-image.md)

## Overview

Build a `shell/linux/Dockerfile` providing a baseline GNU toolbox on a
non-root `ubuntu` base, wire up a CircleCI job that builds it, smoke-tests
it, and publishes it to Docker Hub as `darthjee/tingle:<tag>` on a manual
`v*` git tag push (with an accompanying Docker Hub description-update job),
and document the resulting image reference in `docs/agents/` so sub-issue 2
(`tingle linux` command skeleton) can configure its `docker run` wrapper
against it.

## Agents involved

- [shell](shell.md)
- [architect](architect.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Docker Hub image reference**: `darthjee/tingle:<tag>` (`<tag>` = the
  pushed git tag, e.g. `v1.0.0`). `architect`'s CircleCI job builds
  `shell/linux/Dockerfile` and publishes it under this exact name;
  `product-owner` documents this exact reference for sub-issue 2 to consume.
- **Dockerfile path**: `shell/linux/Dockerfile` — the exact `docker build
  -f` target `architect`'s CircleCI job uses.
- **GNU toolbox packages** installed by `shell`'s Dockerfile: `coreutils`,
  `findutils`, `grep`, `sed` (GNU), `gawk`, `tar`, `diffutils` —
  `architect`'s CI smoke test asserts `sed --version` reports GNU sed as a
  proxy that the right packages landed.
- **Non-root user**: `shell`'s Dockerfile creates a non-root user (uid
  1000, following `python/Dockerfile`'s pattern) — `architect`'s smoke test
  asserts the container does not run as root (e.g. `docker run --rm <image>
  id -u` is not `0`).
