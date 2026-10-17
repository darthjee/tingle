# PHP complexity image for the `tingle code_check php_complexity` command
# (published as darthjee/tingle_php_complexity).
#
# Tingle sends the files to analyse on stdin (one path per line, relative to
# /src) and reads one JSON object on stdout: the merged JSON (tool_versions,
# one files[] entry per input line, warnings). The entrypoint checks every
# accepted file with PHP's own parser, stages the parsable ones under
# /tmp/stage and runs PDepend on that tree, never on /src.
# See entrypoint.php.
#
# Reproducibility:
#   - the PHP base image and the Composer build image are pinned by their
#     multi-platform index digests (linux/amd64 and linux/arm64);
#   - PDepend 3.0.0 and its dependencies are pinned by composer.json +
#     composer.lock (resolved for config.platform.php 8.5.11);
#     `composer validate` fails the build if the lock is stale. The
#     installed tree is pure PHP.
#   See docs/agents/specs/code_check/php_complexity/image.md ("Bumping
#   versions") for the bump procedure.
#
# Build context is this folder, not the repo root:
#   docker buildx build -t <tag> docker/php_complexity
#
# The final stage has no Composer, no zip/unzip, no apt package and no git,
# and runs as uid 1000 by default (no such user exists in the base image;
# the number is enough). Tingle always overrides the user with
# --user <uid>:<gid>.

# Multi-platform index digest of php:8.5.11-cli-trixie (Debian 13 trixie,
# glibc). The final stage builds on it.
ARG BASE_IMAGE=php:8.5.11-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3

# Multi-platform index digest of composer:2.10.3 (PHP 8.5.11). Build only:
# the base image has no zip extension and no unzip, so Composer cannot
# install there.
ARG COMPOSER_IMAGE=composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac

# ---------------------------------------------------------------------------
# deps: installs exactly the locked Composer packages.
# ---------------------------------------------------------------------------
FROM ${COMPOSER_IMAGE} AS deps

WORKDIR /opt/tingle_php_complexity

COPY composer.json composer.lock ./
RUN composer validate --no-check-publish \
 && composer install --no-dev --no-interaction --no-progress --classmap-authoritative

# ---------------------------------------------------------------------------
# final image
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE}

COPY --from=deps /opt/tingle_php_complexity/ /opt/tingle_php_complexity/
COPY entrypoint.php /opt/tingle_php_complexity/

USER 1000:1000

ENTRYPOINT ["php", "/opt/tingle_php_complexity/entrypoint.php"]
