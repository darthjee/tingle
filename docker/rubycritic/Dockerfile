# RubyCritic image for the `tingle code_check rubycritic` command
# (published as darthjee/tingle_rubycritic).
#
# Tingle sends the files to analyse on stdin (one path per line, relative to
# /src) and reads one JSON object on stdout: RubyCritic's report.json plus a
# `parse_errors` key. See entrypoint.rb.
#
# Reproducibility:
#   - the base image is pinned by its multi-platform index digest
#     (linux/amd64 and linux/arm64);
#   - RubyCritic and every gem it pulls in are pinned by Gemfile.lock
#     (platforms aarch64-linux and x86_64-linux), and Bundler runs frozen;
#   - build-essential is pinned to its version in the base image's archive.
#   See docs/agents/specs/code_check/rubycritic/image.md (section 8) for the
#   bump procedure.
#
# Build context is this folder, not the repo root:
#   docker buildx build -t <tag> docker/rubycritic
#
# The final stage has no compiler and no git (RubyCritic then computes no
# churn), keeps the base image's LANG=C.UTF-8, and runs as uid 1000 by
# default. Tingle always overrides the user with --user <uid>:<gid>.

# Multi-platform index digest of ruby:3.3.12-slim (Debian trixie). Both
# stages build on it.
ARG BASE_IMAGE=ruby:3.3.12-slim@sha256:379ffc9ca20cae2655cb80cac53ee23e1e7d859c03a4cceb7f567d6ce4873cee

# ---------------------------------------------------------------------------
# build: compiles the native extensions (prism) and installs the locked gems
# into /usr/local/bundle. The build tools never reach the final image.
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE} AS build

ENV BUNDLE_GEMFILE=/opt/tingle_rubycritic/Gemfile \
    BUNDLE_FROZEN=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential=12.12 \
    && rm -rf /var/lib/apt/lists/*

COPY Gemfile Gemfile.lock /opt/tingle_rubycritic/
RUN bundle install

# ---------------------------------------------------------------------------
# final image
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE}

ENV BUNDLE_GEMFILE=/opt/tingle_rubycritic/Gemfile \
    BUNDLE_FROZEN=true

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY --from=build /opt/tingle_rubycritic/Gemfile /opt/tingle_rubycritic/Gemfile.lock /opt/tingle_rubycritic/
COPY entrypoint.rb /opt/tingle_rubycritic/entrypoint.rb

USER 1000:1000

ENTRYPOINT ["ruby", "/opt/tingle_rubycritic/entrypoint.rb"]
