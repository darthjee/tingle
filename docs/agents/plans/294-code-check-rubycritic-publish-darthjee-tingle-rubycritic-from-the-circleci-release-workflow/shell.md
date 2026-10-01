# Shell Plan: code_check rubycritic: publish darthjee/tingle_rubycritic from the CircleCI release workflow

Main plan: [plan.md](plan.md)

## Shared contracts

- **Script CLI:** `scripts/release_image.sh <subcommand> [linux|rubycritic]`. Subcommands: `setup-builder`, `build`, `smoke-test`, `scan`, `publish`, `update-description`. The selector defaults to `linux`; `setup-builder` ignores it; an unknown selector prints usage on stderr and exits 1.
- **Image:** `darthjee/tingle_rubycritic:<tag>` (one amd64/arm64 manifest). The local per-platform images are `darthjee/tingle_rubycritic:<tag>-<arch>`, loaded and never pushed. The tag comes from `$CIRCLE_TAG`, else `shell/linux/VERSION`, with `verify_version_pin` in CI.
- **No change detection** for `rubycritic`: `build`, `smoke-test`, `scan` and `publish` never skip.
- **CircleCI jobs** (release workflow, same tag filter, `branches: ignore: /.*/`):
  - `build-and-publish-rubycritic-image` (`machine: image: ubuntu-2404:current`, no `requires`)
  - `update-rubycritic-description` (`machine: true`, requires `build-and-publish-rubycritic-image`)
  - `build-and-publish-release` requires both `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`.
- **Docker Hub files:** `docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt` (1-100 chars trimmed) and `docker/rubycritic/DOCKERHUB_DESCRIPTION.md`, both excluded by `docker/rubycritic/.dockerignore`.

## Steps

- [01 — Add the image selector to release_image.sh](shell/01-image-selector.md)
- [02 — Add smoke_test_rubycritic](shell/02-smoke-test-rubycritic.md)
- [03 — Add the Docker Hub description files](shell/03-dockerhub-description-files.md)
- [04 — Add the CircleCI release jobs](shell/04-circleci-jobs.md)

## CI Checks
- No CI job exercises `scripts/` or `docker/` on regular commits. Check locally:
  - `bash -n scripts/release_image.sh` and `shellcheck scripts/release_image.sh` (if installed).
  - `scripts/release_image.sh bogus` and `scripts/release_image.sh build bogus` exit 1 with the usage line.
  - `PLATFORMS=linux/$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/') scripts/release_image.sh build rubycritic`, then `smoke-test rubycritic` (needs Docker; run `setup-builder` first).
  - `circleci config validate` (if the CLI is installed), or at least a YAML parse of `.circleci/config.yml`.

## Notes
- Existing calls without a selector must behave exactly as before. Don't change the linux code paths beyond moving constants into per-image variables.
- Don't run `publish` or `update-description` locally: they push to Docker Hub.
- With no change detection, every tag builds arm64 under QEMU. That's accepted by the spec.
- Release ordering: this must be merged before the tag that ships #295.
