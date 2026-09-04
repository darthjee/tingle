# Plan: Docker: script-ify the tingle-linux release build and add a build-needed check

Issue: [43-docker--script-ify-the-tingle-linux-release-build-and-add-a-build-needed-check.md](../../issues/43-docker--script-ify-the-tingle-linux-release-build-and-add-a-build-needed-check.md)

## Overview

Extract the inline CI bash for the `tingle-linux` Docker release
(`build-and-publish-linux-image` and `update-description` in
`.circleci/config.yml`) into a new `scripts/release_image.sh`, add a
build-needed guard that skips rebuild/republish when `shell/linux/` hasn't
changed since the previous `v*` tag, and close the pre-existing version-pin
drift by making `shell/linux/VERSION` the single source of truth that both
CI and `shell/linux/docker_run.sh` read from, hard-failing CI on any
mismatch against `$CIRCLE_TAG`.

## Agents involved

- [architect](architect.md)
- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **`shell/linux/VERSION`** (new file, owned/created by `shell`): a single
  line containing exactly the release tag, `v`-prefixed (e.g. `v0.0.1`), no
  other content. This is the one source of truth for "what tag is
  currently published."
  - `scripts/release_image.sh` (`architect`) reads this file as the
    default build tag (used for local invocation, where `$CIRCLE_TAG`
    isn't set), and in CI validates that its content matches `$CIRCLE_TAG`
    exactly before allowing any build/publish step to run — a mismatch
    hard-fails the job (non-zero exit), nothing gets built or published.
  - `shell/linux/docker_run.sh` (`shell`) reads this same file to build
    `TINGLE_LINUX_IMAGE="darthjee/tingle:$(cat shell/linux/VERSION)"`,
    replacing the current hardcoded `darthjee/tingle:0.0.1`.
- **Image reference convention**: `darthjee/tingle:<tag>`, where `<tag>` is
  always exactly the content of `shell/linux/VERSION` (or the validated
  `$CIRCLE_TAG` in CI, which must equal it). `architect`'s script,
  `shell`'s `docker_run.sh`, and `product-owner`'s docs must all describe
  this identical convention — no more disagreeing tag formats.
- **Change-detection scope**: `git diff --quiet <prev-tag>..HEAD --
  shell/linux/` — the whole `shell/linux/` directory (not just the
  Dockerfile), so a `shell/linux/VERSION`-only bump still counts as a
  change and correctly triggers a rebuild under the new tag. Implemented
  entirely in `architect`'s script; `shell` doesn't need to do anything
  special here beyond knowing the whole directory is being watched.
