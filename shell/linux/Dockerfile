# GNU toolbox image for the `tingle linux` command.
#
# Provides a baseline of GNU coreutils, findutils, grep, sed, gawk, tar and
# diffutils, running as a non-root user (uid 1000) so files touched through
# a volume mount are owned correctly on the host.
#
# No CMD/ENTRYPOINT is set — every subcommand supplies its own command via
# `docker run <image> <cmd> <args...>`.

# Multi-platform index digest of ubuntu:24.04 (resolves on linux/amd64 and
# linux/arm64).
ARG BASE_IMAGE=ubuntu:24.04@sha256:008173c23f95b170204355c12626cb5a965d779a7e1283b09e9cffbb1bf33ca3

FROM ${BASE_IMAGE}

# snapshot.ubuntu.com date every apt pin below resolves against.
ARG UBUNTU_SNAPSHOT=20260920T000000Z

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Why the bootstrap: the stock sources are plain HTTP, but snapshot.ubuntu.com
# is HTTPS-only, so apt needs a CA bundle before it can reach the snapshot
# (without one, `apt-get update` only warns and silently keeps the live
# archive). ca-certificates is first installed from the live archive, then
# reinstalled — together with its openssl dependency — at the snapshot's
# version (hence --allow-downgrades), so the final image only carries
# snapshot versions.
#
# apt has no built-in snapshot mapping for ports.ubuntu.com (the arm64
# mirror), so it is pointed at snapshot.ubuntu.com/ubuntu, which serves every
# architecture. --error-on=any turns fetch warnings into a failed build.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && echo 'Acquire::Snapshots::URI::Host::ports.ubuntu.com "https://snapshot.ubuntu.com/ubuntu/@SNAPSHOTID@/";' \
        > /etc/apt/apt.conf.d/99snapshot-ports \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update --error-on=any --snapshot "$UBUNTU_SNAPSHOT" \
    && apt-get install -y --no-install-recommends --allow-downgrades \
        --snapshot "$UBUNTU_SNAPSHOT" \
        ca-certificates=20260601~24.04.1 \
        openssl=3.0.13-0ubuntu3.15 \
        coreutils=9.4-3ubuntu6.3 \
        findutils=4.9.0-5build1 \
        grep=3.11-4build1 \
        sed=4.9-2ubuntu0.24.04.1 \
        gawk=1:5.2.1-2ubuntu0.1 \
        tar=1.35+dfsg-3ubuntu0.4 \
        diffutils=1:3.10-1ubuntu0.1 \
    && rm -rf /var/lib/apt/lists/*

RUN userdel --remove ubuntu 2>/dev/null; \
    useradd --create-home --uid 1000 tingle
USER tingle
