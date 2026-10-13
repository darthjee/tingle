# Issue: code_check js_complexity: publish darthjee/tingle_js_complexity from the CircleCI release workflow

## Description
Publish `darthjee/tingle_js_complexity:<tag>` for `linux/amd64` and `linux/arm64` from the CircleCI `release` workflow on every tingle git tag, next to `darthjee/tingle` and `darthjee/tingle_rubycritic` (parent #315). The image itself already exists under `docker/js_complexity/` (#318).

Spec: `docs/agents/specs/code_check/js_complexity/release.md`.

## Problem
`tingle code_check js_complexity` defaults to `darthjee/tingle_js_complexity:<tingle version>`. That tag must exist on Docker Hub before a tingle release ships the subcommand (#320). Otherwise the CLI points at an image that was never published.

## Expected Behavior
- `scripts/release_image.sh` accepts a third selector, `js_complexity`, for `build`, `smoke-test`, `scan`, `publish` and `update-description`. Its settings in `select_image()` are:
  - image `darthjee/tingle_js_complexity`;
  - Dockerfile `docker/js_complexity/Dockerfile`;
  - build context `docker/js_complexity`;
  - no change detection (always runs), like rubycritic;
  - smoke-test function `smoke_test_js_complexity`;
  - description files `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` and `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`.

  The `USAGE` line and the header table are updated. `setup-builder` still ignores the selector.
- **Compatibility:** with no selector, the script still uses `linux`. `linux` and `rubycritic` behave exactly as before. An unknown selector still prints the usage on stderr and exits 1.
- **Smoke test:** on each platform, `smoke_test_js_complexity` runs the local `<tag>-<arch>` image with the canonical run line (`--pull never --network none --security-opt no-new-privileges`, `-v docker/js_complexity/fixture:/src:ro`, `--user 501:20`). It feeds the fixture list and the hostile lines on stdin. `python3` checks that the output is valid JSON, that it lists the expected files, and that the syntax-error fixture has a parse-error marker. The test also checks that the image has no git and that empty stdin gives empty `files` and `warnings`. A failed check prints `<reason> on <platform>` and exits 1.
- **Publish:** one multi-platform manifest per tag. `publish` fails unless `docker buildx imagetools inspect` lists every platform in `$PLATFORMS`. No `latest` tag and no per-arch tags are pushed.
- **CircleCI:** `.circleci/config.yml` adds `build-and-publish-js-complexity-image` (`machine: image: ubuntu-2404:current`) and `update-js-complexity-description` (`machine: true`, requires the build job) to the `release` workflow. Both mirror the rubycritic jobs and use the same tag filter and `branches: ignore: /.*/`. `build-and-publish-release` (the CLI zip) now **also requires** `build-and-publish-js-complexity-image`. The `test` workflow does not change.
- **Docker Hub files:** `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` (one line, 1–100 chars) and `DOCKERHUB_DESCRIPTION.md` are written. For now they describe FTA only. `docker/js_complexity/.dockerignore` also excludes both files.
- **Docs:** `docs/agents/tingle-js-complexity-image.md` covers the header bullets, the contract, the runtime user and hardening, the release pipeline, the Docker Hub description, the local build (`make js-complexity-image`) and version bumps. It follows the style of `docs/agents/tingle-rubycritic-image.md`. `tingle-linux-image.md` and `tingle-rubycritic-image.md` each get a one-line pointer to it, and their "a git tag triggers the image jobs" note now lists the js_complexity jobs.

## Solution
Extend the existing script and workflow; there is no new release script. Tags are resolved the same way as for the other images: `$CIRCLE_TAG` in CI, `shell/linux/VERSION` locally. A mismatch is a hard failure (`verify_version_pin`). The slow QEMU arm64 build (FTA compiles Rust) is accepted.

**Ordering:** this must be merged before the tingle tag that ships the `js_complexity` subcommand (#320) is pushed.

### Out of scope
- jscpd (#324), escomplex (#325) and SFC (#326) additions. Those sub-issues extend the smoke test and the Docker Hub description in the same PR as their image change.

### Agents
- `shell`: `scripts/release_image.sh`, `.circleci/config.yml`, the Docker Hub files, `docker/js_complexity/.dockerignore`.
- `product-owner`: `docs/agents/tingle-js-complexity-image.md` and the pointers in the two existing image docs.

## Benefits
- The CLI and its three images are always released together under the same tag, and the CLI zip is never published without them.
