# Plan: release: build-and-publish-linux-image fails in "Set up builder" — builder does not see arm64 after QEMU registration

Issue: [243-release-build-and-publish-linux-image-fails-in-set-up-builder-builder-does-not-see-arm64-after-qemu-registration.md](../../issues/243-release-build-and-publish-linux-image-fails-in-set-up-builder-builder-does-not-see-arm64-after-qemu-registration.md)

## Overview
`scripts/release_image.sh setup-builder` starts the `tingle-builder` BuildKit container before registering QEMU. BuildKit only works out which platforms it can emulate when its worker starts, so the re-check after `binfmt --install` sees an out-of-date list and fails on arm64. The fix: after registering QEMU, stop the builder so the next `inspect --bootstrap` starts it again, and fall back to removing and recreating it once. A new `setup-builder` job in the `test` workflow runs this path on every PR. The agent doc that describes the setup order wrongly is corrected.

## Agents involved

- [shell](shell.md): `scripts/release_image.sh` and `.circleci/config.yml`. Neither `scripts/` nor `.circleci/` has a dedicated owner, so both go to the Bash specialist.
- [product-owner](product-owner.md): `docs/agents/tingle-linux-image.md`.

## Shared contracts

The steps of `setup-builder`, which the script must implement and the doc must describe word for word:

1. Create `tingle-builder` (`--driver docker-container`) if it doesn't exist.
2. Start it and check its platforms (`docker buildx inspect --bootstrap`). If every platform in `$PLATFORMS` is listed, register nothing, restart nothing, and print `Builder tingle-builder ready for: <csv>`. This is the Docker Desktop and re-run path, and no privileged container runs.
3. Otherwise, register QEMU for the missing architectures with `docker run --privileged --rm tonistiigi/binfmt:qemu-v10.2.3 --install <archs>`.
4. Print `Restarting builder tingle-builder to detect new platforms`, run `docker buildx stop tingle-builder`, then check again (this starts it again).
5. If platforms are still missing, print `Recreating builder tingle-builder to detect new platforms`, run `docker buildx rm` + `docker buildx create --name tingle-builder --driver docker-container`, then check once more. Only this path loses the builder's cache.
6. If platforms are still missing, fail with `Builder tingle-builder still does not support: <archs>` on stderr, exit 1.

Other things both agents rely on:
- The builder is never "selected" (`docker buildx use`). `build` and `publish` pass `--builder tingle-builder`.
- Stopping the builder interrupts any build using it at that moment. This only happens locally, and only when QEMU was missing.
- The new CI job is called `setup-builder`, is in the `test` workflow, and runs on `machine: image: ubuntu-2404:current`.
