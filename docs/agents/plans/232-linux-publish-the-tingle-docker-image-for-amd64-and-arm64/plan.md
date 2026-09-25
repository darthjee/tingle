# Plan: linux: publish the tingle Docker image for amd64 and arm64

Issue: [232-linux-publish-the-tingle-docker-image-for-amd64-and-arm64.md](../../issues/232-linux-publish-the-tingle-docker-image-for-amd64-and-arm64.md)

## Overview
Publish `darthjee/tingle` as one multi-platform tag (`linux/amd64` + `linux/arm64`), built on the existing amd64 CircleCI machine with QEMU emulation.

- The `shell` agent reworks `scripts/release_image.sh`: `build` loads each platform locally, `smoke-test` runs against both, and `publish` does one multi-platform `buildx --push`. It also adds a builder/QEMU setup subcommand, pins the CircleCI machine image and adds a CI step.
- The `product-owner` agent documents the new flow in `docs/agents/tingle-linux-image.md`.

**Prerequisite:** #233 must be merged first. Its `kubectl` and AWS CLI downloads pick the architecture from `TARGETARCH`, so the Dockerfile needs no further change here.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

`scripts/release_image.sh` interface, after this change:

| Subcommand | Behaviour |
|---|---|
| `setup-builder` (new) | Idempotent. Registers QEMU/binfmt for every non-native platform in `PLATFORMS` (`docker run --privileged --rm tonistiigi/binfmt:<pinned> --install <arch,...>`), then creates and selects a buildx builder named `tingle-builder` with the `docker-container` driver (`docker buildx inspect tingle-builder` or `docker buildx create --name tingle-builder --driver docker-container --use`). It skips the binfmt install when every platform is already listed by `docker buildx inspect --bootstrap`, as on Docker Desktop. |
| `build` | For each platform `p` in `PLATFORMS`: `docker buildx build --builder tingle-builder --platform $p --load -t darthjee/tingle:<tag>-<arch> -f shell/linux/Dockerfile .`, where `<arch>` is `${p#linux/}` (`amd64`, `arm64`). Local tags only; never pushed. |
| `smoke-test` | Runs every existing check (sed, non-root, plus whatever #233 and #234 added, including the report-only Trivy scan) against each `darthjee/tingle:<tag>-<arch>`, with `--platform $p` on every `docker run`. Fails if any platform fails. |
| `publish` | `verify_version_pin`, then log in, then `docker buildx build --builder tingle-builder --platform <PLATFORMS comma-joined> --push -t darthjee/tingle:<tag> -f shell/linux/Dockerfile .` (reusing the builder cache from `build`), then `docker buildx imagetools inspect darthjee/tingle:<tag>`, which must list every platform or the job fails. |
| `update-description` | Unchanged. |

- `PLATFORMS` is an env var, space-separated, defaulting to `linux/amd64 linux/arm64`. Setting it (for example `PLATFORMS=linux/arm64`) builds and tests only those platforms locally.
- `build`, `smoke-test` and `publish` keep the `changed_since_previous` early exit. `build` and `publish` keep `verify_version_pin`.
- **Tags:** only `darthjee/tingle:<semver>` ever reaches Docker Hub. `<tag>-<arch>` exists only in the local daemon.
- **CI order** (job `build-and-publish-linux-image`, in one job so the builder cache is shared): `setup-builder`, `build`, `smoke-test`, `publish`.
