# JS/TS complexity image for the `tingle code_check js_complexity` command
# (published as darthjee/tingle_js_complexity).
#
# Tingle sends the files to analyse on stdin (one path per line, relative to
# /src) and reads one JSON object on stdout: the merged JSON (tool_versions,
# one files[] entry per input line, warnings). The entrypoint stages the
# accepted files under /tmp/stage and runs FTA on that tree, never on /src.
# See entrypoint.js.
#
# Reproducibility:
#   - the Node base image and the Rust build image are pinned by their
#     multi-platform index digests (linux/amd64 and linux/arm64);
#   - FTA 3.1.0 is built from the `fta` crate with `cargo install --locked`,
#     so every Rust dependency is pinned by the crate's own Cargo.lock
#     (the fta-cli npm package's arm64 binary needs musl, so it is not used);
#   - the npm tools are pinned by package.json + package-lock.json, and
#     `npm ci` fails if they disagree.
#   See docs/agents/specs/code_check/js_complexity/image.md ("Bumping
#   versions") for the bump procedure.
#
# Build context is this folder, not the repo root:
#   docker buildx build -t <tag> docker/js_complexity
#
# The final stage has no Rust toolchain, no apt package and no git, and runs
# as uid 1000 (the base image's `node` user) by default. Tingle always
# overrides the user with --user <uid>:<gid>.

# Multi-platform index digest of node:24.21.0-slim (Debian 12 bookworm,
# glibc). The deps and final stages build on it.
ARG BASE_IMAGE=node:24.21.0-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20

# Multi-platform index digest of rust:1.99.0-slim-bookworm. Build only.
ARG RUST_IMAGE=rust:1.99.0-slim-bookworm@sha256:2c3a22f0a5533ea2dd5a16627bc841228151faa2d4de2644ac9987e4a2f1f2fa

# ---------------------------------------------------------------------------
# fta: builds FTA from the `fta` crate. The result, /opt/fta/bin/fta, links
# only against glibc (libgcc_s, libm, libc), which the Debian base provides.
# ---------------------------------------------------------------------------
FROM ${RUST_IMAGE} AS fta

RUN cargo install fta --version 3.1.0 --locked --root /opt/fta

# ---------------------------------------------------------------------------
# deps: installs exactly the locked npm tools.
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE} AS deps

WORKDIR /opt/tingle_js_complexity

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

# ---------------------------------------------------------------------------
# final image
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE}

COPY --from=fta /opt/fta/bin/fta /usr/local/bin/fta
COPY --from=deps /opt/tingle_js_complexity/ /opt/tingle_js_complexity/
COPY entrypoint.js /opt/tingle_js_complexity/

USER 1000:1000

ENTRYPOINT ["node", "/opt/tingle_js_complexity/entrypoint.js"]
