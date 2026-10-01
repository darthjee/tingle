# Plan: code_check rubycritic: publish darthjee/tingle_rubycritic from the CircleCI release workflow

Issue: [294-code-check-rubycritic-publish-darthjee-tingle-rubycritic-from-the-circleci-release-workflow.md](../../issues/294-code-check-rubycritic-publish-darthjee-tingle-rubycritic-from-the-circleci-release-workflow.md)

## Overview
`scripts/release_image.sh` gains an image selector (`linux|rubycritic`, default `linux`). The `rubycritic` selector builds, smoke-tests, scans and publishes `darthjee/tingle_rubycritic:X.Y.Z` from `docker/rubycritic/` on every release tag, with no change detection. CircleCI gets two release jobs, and the CLI zip waits for both images. `shell` also adds the Docker Hub description files. `product-owner` documents the image in `docs/agents/tingle-rubycritic-image.md`. The spec is [release.md](../../specs/code_check/rubycritic/release.md).

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Script CLI:** `scripts/release_image.sh <subcommand> [linux|rubycritic]`. Subcommands: `setup-builder`, `build`, `smoke-test`, `scan`, `publish`, `update-description`. The selector defaults to `linux`; `setup-builder` ignores it; an unknown selector prints usage on stderr and exits 1.
- **Image:** `darthjee/tingle_rubycritic:<tag>` (one amd64/arm64 manifest). The local per-platform images are `darthjee/tingle_rubycritic:<tag>-<arch>`, loaded and never pushed. The tag comes from `$CIRCLE_TAG`, else `shell/linux/VERSION`, with `verify_version_pin` in CI.
- **No change detection** for `rubycritic`: `build`, `smoke-test`, `scan` and `publish` never skip.
- **CircleCI jobs** (release workflow, same tag filter, `branches: ignore: /.*/`):
  - `build-and-publish-rubycritic-image` (`machine: image: ubuntu-2404:current`, no `requires`)
  - `update-rubycritic-description` (`machine: true`, requires `build-and-publish-rubycritic-image`)
  - `build-and-publish-release` requires both `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`.
- **Docker Hub files:** `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` (1-100 chars trimmed) and `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`, both excluded by `docker/rubycritic/.dockerignore`.
