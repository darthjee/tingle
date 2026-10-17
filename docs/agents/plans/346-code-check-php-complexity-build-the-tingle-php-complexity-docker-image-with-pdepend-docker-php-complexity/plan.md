# Plan: code_check php_complexity: build the tingle_php_complexity Docker image with PDepend (docker/php_complexity/)

Issue: [346-code-check-php-complexity-build-the-tingle-php-complexity-docker-image-with-pdepend-docker-php-complexity.md](../../issues/346-code-check-php-complexity-build-the-tingle-php-complexity-docker-image-with-pdepend-docker-php-complexity.md)

## Overview
Add `docker/php_complexity/`, the `tingle_php_complexity` image. It is a two-stage build (a pinned Composer stage installs PDepend 3.0.0, and the final stage is `php:8.5.11-cli-trixie`). Its PHP entrypoint reads a file list on stdin, runs a PHP parse check, runs PDepend over a staged copy in `/tmp` and prints one merged JSON document. The normative source is [image.md](../../specs/code_check/php_complexity/image.md), and every step implements that spec exactly. The layout follows `docker/js_complexity/` (#318).

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Folder:** `docker/php_complexity/`, owned by the `shell` agent, with build context `docker/php_complexity`.
- **Local tag:** `tingle_php_complexity:dev`, built by `make php-complexity-image`.
- **Long-form image doc:** `docs/agents/tingle-php-complexity-image.md` does **not** exist yet (#347 adds it). Until then, both the folder-structure entry and the `shell` agent scope link to `docs/agents/specs/code_check/php_complexity/image.md`. #347 retargets those links.
