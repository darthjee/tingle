# Shell Plan: linux: publish the tingle Docker image for amd64 and arm64

Main plan: [plan.md](plan.md)

## Shared contracts

- Implement the `scripts/release_image.sh` interface in [plan.md](plan.md#shared-contracts) exactly: the `setup-builder` subcommand, the `PLATFORMS` env var (default `linux/amd64 linux/arm64`), the builder name `tingle-builder`, local tags `darthjee/tingle:<tag>-<arch>`, and one multi-platform `darthjee/tingle:<tag>` pushed in `publish`.
- The `product-owner` agent documents this interface. Keep the header comment of `scripts/release_image.sh` consistent with it.

## Steps

- [01 — Builder and QEMU setup](shell/01-setup-builder.md)
- [02 — Per-platform build and smoke test](shell/02-per-platform-build-and-smoke-test.md)
- [03 — Multi-platform publish](shell/03-multi-platform-publish.md)
- [04 — CircleCI job and Docker Hub description](shell/04-circleci-and-dockerhub-description.md)

## CI Checks
- The release job `build-and-publish-linux-image` only runs on semver tags. Before merging, run it locally on the branch:
  `scripts/release_image.sh setup-builder && scripts/release_image.sh build && scripts/release_image.sh smoke-test`.
  - Without a tag, the tag resolves from `shell/linux/VERSION`.
  - `changed_since_previous` may skip everything when `shell/linux/` is unchanged since the last tag. Temporarily test with a branch that touches `shell/linux/`, or call the functions directly.
- `shellcheck scripts/release_image.sh` (Codacy runs ShellCheck).

## Notes
- **Dependency:** #233 must be merged first. `TARGETARCH`-based downloads are needed, otherwise the arm64 image would contain amd64 `kubectl`/`aws` binaries. If this plan is implemented before #233, the current Dockerfile (apt only) still builds for arm64 as is.
- **apt pins:** one pin list for both architectures (the issue's decision). On arm64, apt uses `ports.ubuntu.com`. Verify that `apt-get update --snapshot` works there. If a pin is missing on arm64, the build fails loudly; fix that pin rather than introducing per-architecture pins.
- The arm64 build under QEMU is slow (apt, AWS CLI unzip). That's accepted, because it only runs on release tags.
- `--load` of a single platform works with the `docker-container` driver. A multi-platform `--load` would not, which is why `build` loops over platforms.
- Pin `tonistiigi/binfmt` to a specific tag, like every other pin in the image pipeline.
