# Issue: code_check php_complexity: publish darthjee/tingle_php_complexity from the CircleCI release workflow

## Description
Publish the `darthjee/tingle_php_complexity` image (parent #344) from the CircleCI `release` workflow, next to `darthjee/tingle`, `darthjee/tingle_rubycritic` and `darthjee/tingle_js_complexity`. It uses the same plain semver tag as tingle (no `latest`, `v`-prefixed tags ignored) and is published as one multi-arch manifest (amd64/arm64).

**Normative spec:** `docs/agents/specs/code_check/php_complexity/release.md` (written by #345). It is the source of truth for every detail below.

Depends on #346 (`docker/php_complexity/`, already merged).

## Problem
At runtime, tingle defaults to `darthjee/tingle_php_complexity:<tingle version>`. That tag has to exist on Docker Hub before a tingle release ships the subcommand (#348). Otherwise the CLI would point at an image tag that was never published. **Ordering rule:** #347 must be merged before the release tag that ships #348 is pushed.

## Expected Behavior
- **`scripts/release_image.sh`** gets a fourth selector, `php_complexity`, next to `linux|rubycritic|js_complexity`. Its settings (image name, Dockerfile, build context, smoke test, Docker Hub description files) go in a new `select_image()` case. The `USAGE` line, the usage comments and the header settings table list the new selector. There is no new script.
  - **No change detection:** every release tag builds, smoke-tests, scans and publishes the image.
  - **Compatibility:** no selector still means `linux`, the existing three selectors behave exactly as before, and an unknown selector prints usage and exits 1.
- **`smoke_test_php_complexity`** is laid out like `smoke_test_js_complexity`. For each platform, it pipes the 19 fixture files and the hostile lines through the canonical hardened run line as user `501:20`, then checks the JSON with `python3`. It checks the #346 expectations: `functions`, `duplication` and `tool_versions.jscpd` are all `null`. It also checks that git is absent, and that empty stdin gives empty `files` and `warnings`. Any failure prints `<reason> on <platform>` and exits 1.
- **`.circleci/config.yml`** gets `build-and-publish-php-complexity-image` (`ubuntu-2404:current`: setup-builder, build, smoke-test, scan, publish) and `update-php-complexity-description` (`machine: true`, requires the build job). Both mirror the js_complexity jobs and use the same tag filter. `build-and-publish-release` now also requires `build-and-publish-php-complexity-image`. The `test` workflow is unchanged.
- **Docker Hub files** (owned by `shell`): `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` (1–100 chars) and `DOCKERHUB_DESCRIPTION.md`. Until #352 lands, both list PHP and PDepend only. `docker/php_complexity/.dockerignore` also excludes both files.
- **Docs** (owned by `product-owner`): new `docs/agents/tingle-php-complexity-image.md`, in the style of `tingle-js-complexity-image.md`, with the seven sections of spec §6. `tingle-linux-image.md`, `tingle-rubycritic-image.md` and `tingle-js-complexity-image.md` get a pointer to it, and their notes on git-tag-triggered jobs list the php_complexity jobs.
- **Verification:** `bash -n` and `shellcheck` pass. `build php_complexity` and `smoke-test php_complexity` pass locally for both platforms. `smoke-test bogus` prints usage and exits 1.

## Solution
Copy the js_complexity release wiring and adapt it. Keep the job structure and naming parallel, so all four images are released the same way.

### Out of scope
- Any change to the image's contents (`Dockerfile`, entrypoint, lib, fixture) or to the Python side.
- The smoke-test and description changes for `--details` (#351) and jscpd (#352). Those land in their own PRs.
