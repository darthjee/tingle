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
#     installed tree is pure PHP;
#   - the Node build image is pinned by its multi-platform index digest (the
#     same one as docker/js_complexity/);
#   - jscpd 5.4.1 is pinned by package.json + package-lock.json, and
#     `npm ci` fails if they disagree. jscpd is a Rust binary shipped as
#     per-platform optional npm packages; the lock lists both
#     jscpd-linux-x64-gnu and jscpd-linux-arm64-gnu, and `npm ci` installs
#     the one matching the build platform. Only that native binary is
#     copied into the final stage, as /usr/local/bin/jscpd.
#   See docs/agents/specs/code_check/php_complexity/image.md ("Bumping
#   versions") for the bump procedure.
#
# Build context is this folder, not the repo root:
#   docker buildx build -t <tag> docker/php_complexity
#
# The final stage has no Composer, no zip/unzip, no Node, no node_modules,
# no apt package and no git, and runs as uid 1000 by default (no such user
# exists in the base image; the number is enough). Tingle always overrides
# the user with --user <uid>:<gid>.

# Multi-platform index digest of php:8.5.11-cli-trixie (Debian 13 trixie,
# glibc). The final stage builds on it.
ARG BASE_IMAGE=php:8.5.11-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3

# Multi-platform index digest of composer:2.10.3 (PHP 8.5.11). Build only:
# the base image has no zip extension and no unzip, so Composer cannot
# install there.
ARG COMPOSER_IMAGE=composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac

# Multi-platform index digest of node:24.21.0-slim (Debian 12 bookworm,
# glibc), the same as docker/js_complexity/. Build only: the final stage
# gets jscpd's native binary, never Node.
ARG NODE_IMAGE=node:24.21.0-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20

# ---------------------------------------------------------------------------
# deps: installs exactly the locked Composer packages.
# ---------------------------------------------------------------------------
FROM ${COMPOSER_IMAGE} AS deps

WORKDIR /opt/tingle_php_complexity

COPY composer.json composer.lock ./
RUN composer validate --no-check-publish \
 && composer install --no-dev --no-interaction --no-progress --classmap-authoritative

# ---------------------------------------------------------------------------
# jscpd: installs the locked jscpd and keeps only its native binary. The
# npm package's `jscpd` bin is a Node launcher (run-jscpd.js) that spawns
# node_modules/jscpd-linux-<arch>-gnu/bin/jscpd; that binary links only
# against glibc (libgcc_s, libm, libc), which the Debian base provides.
# The `test` fails the build unless exactly one platform package is
# installed.
# ---------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS jscpd

WORKDIR /opt/jscpd

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund \
 && test "$(ls -d node_modules/jscpd-linux-*-gnu | wc -l)" -eq 1 \
 && cp node_modules/jscpd-linux-*-gnu/bin/jscpd /opt/jscpd/jscpd

# ---------------------------------------------------------------------------
# final image
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE}

COPY --from=jscpd /opt/jscpd/jscpd /usr/local/bin/jscpd
COPY --from=deps /opt/tingle_php_complexity/ /opt/tingle_php_complexity/
COPY entrypoint.php /opt/tingle_php_complexity/
COPY lib/ /opt/tingle_php_complexity/lib/

USER 1000:1000

ENTRYPOINT ["php", "/opt/tingle_php_complexity/entrypoint.php"]
