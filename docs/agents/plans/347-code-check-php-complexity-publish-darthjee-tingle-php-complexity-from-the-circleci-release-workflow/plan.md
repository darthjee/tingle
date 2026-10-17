# Plan: code_check php_complexity: publish darthjee/tingle_php_complexity from the CircleCI release workflow

Issue: [347](../../../issues/347-code-check-php-complexity-publish-darthjee-tingle-php-complexity-from-the-circleci-release-workflow.md)

## Overview
Wire the existing `docker/php_complexity/` image (#346) into the release pipeline, mirroring the js_complexity one (#319): add a `php_complexity` selector and a scripted smoke test to `scripts/release_image.sh`, add two CircleCI release jobs, add the Docker Hub description files, and document the image in `docs/agents/tingle-php-complexity-image.md`. The normative spec is [release.md](../../specs/code_check/php_complexity/release.md); the image and fixture details it relies on are in [image.md](../../specs/code_check/php_complexity/image.md).

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Selector:** `php_complexity`, the fourth value of `scripts/release_image.sh <subcommand> [linux|rubycritic|js_complexity|php_complexity]`. Image `darthjee/tingle_php_complexity`, Dockerfile `docker/php_complexity/Dockerfile`, build context `docker/php_complexity`, no change detection, smoke test `smoke_test_php_complexity`.
- **Tag:** plain semver `X.Y.Z` from `$CIRCLE_TAG` / `shell/linux/VERSION`; every release tag publishes; no `latest`; one amd64/arm64 manifest.
- **CircleCI jobs:** `build-and-publish-php-complexity-image` (`machine: image: ubuntu-2404:current`; steps `Set up builder`, `Build image`, `Smoke test`, `Scan image`, `Publish image`) and `update-php-complexity-description` (`machine: true`, requires the build job). `build-and-publish-release` requires all four image jobs.
- **Docker Hub files:** `docker/php_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` (one line, 1–100 chars) and `docker/php_complexity/DOCKERHUB_DESCRIPTION.md`. They list PHP and PDepend only (jscpd comes with #352).
- **Smoke-test checks (#346 state):** 19 fixture files then hostile lines `("" /etc/passwd ../outside.php Calculator.php missing.php notes.txt)`, run as `501:20` with `--network none` and read-only `/src`; `functions`, `duplication` and `tool_versions.jscpd` all `null`; no git; empty stdin → `"files": []`, `"warnings": []`, exit 0. Failures print `<reason> on <platform>` and exit 1.
