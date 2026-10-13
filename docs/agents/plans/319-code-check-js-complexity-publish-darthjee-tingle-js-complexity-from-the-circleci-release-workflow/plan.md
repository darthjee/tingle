# Plan: code_check js_complexity: publish darthjee/tingle_js_complexity from the CircleCI release workflow

Issue: [319-code-check-js-complexity-publish-darthjee-tingle-js-complexity-from-the-circleci-release-workflow.md](../../issues/319-code-check-js-complexity-publish-darthjee-tingle-js-complexity-from-the-circleci-release-workflow.md)

## Overview
Add a third image selector, `js_complexity`, to `scripts/release_image.sh` (no change detection, its own smoke test and Docker Hub files). Add two matching CircleCI release jobs and make the CLI release zip depend on the new image job, so that `darthjee/tingle_js_complexity:X.Y.Z` (one amd64/arm64 manifest) is published on every tingle tag. Document the image in `docs/agents/tingle-js-complexity-image.md`. The normative source is `docs/agents/specs/code_check/js_complexity/release.md`, with the smoke-test expectations in `image.md` §9.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Selector:** `scripts/release_image.sh <subcommand> [linux|rubycritic|js_complexity]`. With no selector, the script still uses `linux`. An unknown selector prints `USAGE` on stderr and exits 1.
- **`js_complexity` settings:** image `darthjee/tingle_js_complexity`, Dockerfile `docker/js_complexity/Dockerfile`, context `docker/js_complexity`, `CHANGE_DETECTION_PATH=""` (never skips), smoke test `smoke_test_js_complexity`, description files `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` and `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`.
- **CircleCI job names:** `build-and-publish-js-complexity-image` (`machine: image: ubuntu-2404:current`; steps `setup-builder`, `build`, `smoke-test`, `scan` and `publish`, each with `js_complexity`) and `update-js-complexity-description` (`machine: true`, requires the build job). `build-and-publish-release` requires all three image jobs.
- **Smoke-test checks** (to be documented by product-owner exactly as shell implements them): fixture list plus the five hostile lines on stdin; exit 0; one JSON object; `tool_versions.fta == "3.1.0"` and jscpd/escomplex `null`; `files[i].path` matches input line `i`; the FTA column of the image.md §9 table; hostile lines get `fta: null`, `parse_error: false` and an `entrypoint` warning; no git in the image; empty stdin gives empty `files` and `warnings`. Failures print `<reason> on <platform>`.
