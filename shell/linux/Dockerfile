# GNU toolbox image for the `tingle linux` command.
#
# Provides a baseline of GNU coreutils, findutils, grep, sed, gawk, tar and
# diffutils, running as a non-root user (uid 1000) so files touched through
# a volume mount are owned correctly on the host.
#
# No CMD/ENTRYPOINT is set — every subcommand supplies its own command via
# `docker run <image> <cmd> <args...>`.

# Multi-platform index digest of ubuntu:24.04 (resolves on linux/amd64 and
# linux/arm64). Both stages build on it.
ARG BASE_IMAGE=ubuntu:24.04@sha256:008173c23f95b170204355c12626cb5a965d779a7e1283b09e9cffbb1bf33ca3

# snapshot.ubuntu.com date every apt pin (in both stages) resolves against.
ARG UBUNTU_SNAPSHOT=20260920T000000Z

# ---------------------------------------------------------------------------
# fetch: downloads and verifies the upstream tools. Nothing from this stage
# reaches the final image except /out/kubectl and /usr/local/aws-cli.
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE} AS fetch
ARG UBUNTU_SNAPSHOT
ARG TARGETARCH
ARG KUBECTL_VERSION=1.37.1
ARG AWS_CLI_VERSION=2.37.4

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Same ca-certificates bootstrap and ports.ubuntu.com mapping as the final
# stage (see the comment there).
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
        curl=8.5.0-2ubuntu10.13 \
        gpg=2.4.4-2ubuntu17.6 \
        libssl3t64=3.0.13-0ubuntu3.15 \
        openssl=3.0.13-0ubuntu3.15 \
        unzip=6.0-28ubuntu4.1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/fetch

# kubectl, checked against the upstream SHA-256.
RUN arch="${TARGETARCH:-$(dpkg --print-architecture)}" \
    && base="https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${arch}" \
    && curl -fsSL --proto '=https' -o kubectl "${base}/kubectl" \
    && curl -fsSL --proto '=https' -o kubectl.sha256 "${base}/kubectl.sha256" \
    && echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check --strict \
    && install -D -m 0755 kubectl /out/kubectl \
    && rm -f kubectl kubectl.sha256

# AWS CLI v2 public key, copied from the AWS CLI install guide.
#   Fingerprint: FB5D B77F D5C1 18B8 0511  ADA8 A631 0ACC 4672 475C
#   Expires:     2027-07-01
COPY shell/linux/aws-cli.asc /tmp/aws-cli.asc

# AWS CLI v2, checked against its PGP signature. gpg only dearmors the key
# (importing it would need gpg-agent); gpgv does the verification into a
# throwaway keyring. The VALIDSIG check also pins the primary key
# fingerprint, so a swapped key file fails the build.
RUN arch="${TARGETARCH:-$(dpkg --print-architecture)}" \
    && case "$arch" in \
        amd64) aws_arch=x86_64 ;; \
        arm64) aws_arch=aarch64 ;; \
        *) echo "unsupported architecture: $arch" >&2; exit 1 ;; \
    esac \
    && url="https://awscli.amazonaws.com/awscli-exe-linux-${aws_arch}-${AWS_CLI_VERSION}.zip" \
    && curl -fsSL --proto '=https' -o awscliv2.zip "$url" \
    && curl -fsSL --proto '=https' -o awscliv2.sig "${url}.sig" \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && gpg --batch --dearmor --output aws-cli.gpg /tmp/aws-cli.asc \
    && gpgv --keyring ./aws-cli.gpg --status-fd 1 awscliv2.sig awscliv2.zip \
        | grep '^\[GNUPG:\] VALIDSIG .* FB5DB77FD5C118B80511ADA8A6310ACC4672475C$' >/dev/null \
    && unzip -q awscliv2.zip \
    && ./aws/install --install-dir /usr/local/aws-cli --bin-dir /out/bin \
    && rm -rf "$GNUPGHOME" aws-cli.gpg awscliv2.zip awscliv2.sig aws

# ---------------------------------------------------------------------------
# final image
# ---------------------------------------------------------------------------
FROM ${BASE_IMAGE}
ARG UBUNTU_SNAPSHOT

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Why the bootstrap: the stock sources are plain HTTP, but snapshot.ubuntu.com
# is HTTPS-only, so apt needs a CA bundle before it can reach the snapshot
# (without one, `apt-get update` only warns and silently keeps the live
# archive). ca-certificates is first installed from the live archive, then
# reinstalled — together with openssl and libssl3t64 — at the snapshot's
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
        # baseline GNU toolbox
        coreutils=9.4-3ubuntu6.3 \
        diffutils=1:3.10-1ubuntu0.1 \
        findutils=4.9.0-5build1 \
        gawk=1:5.2.1-2ubuntu0.1 \
        grep=3.11-4build1 \
        sed=4.9-2ubuntu0.24.04.1 \
        tar=1.35+dfsg-3ubuntu0.4 \
        # ca-certificates dependencies, re-pinned after the bootstrap
        libssl3t64=3.0.13-0ubuntu3.15 \
        openssl=3.0.13-0ubuntu3.15 \
        # git and friends
        ca-certificates=20260601~24.04.1 \
        git=1:2.43.0-1ubuntu7.3 \
        less=590-2ubuntu2.1 \
        openssh-client=1:9.6p1-3ubuntu13.19 \
        # data and network
        curl=8.5.0-2ubuntu10.13 \
        dnsutils=1:9.18.39-0ubuntu0.24.04.7 \
        iproute2=6.1.0-1ubuntu6.4 \
        iputils-ping=3:20240117-1ubuntu0.1 \
        jq=1.7.1-3ubuntu0.24.04.2 \
        netcat-openbsd=1.226-1ubuntu2 \
        wget=1.21.4-1ubuntu4.5 \
        # editing, search and viewing
        bash-completion=1:2.11-8 \
        bat=0.24.0-1build1 \
        fd-find=9.0.0-1 \
        file=1:5.45-3build1 \
        ripgrep=14.1.0-1 \
        tree=2.1.1-2ubuntu3.24.04.2 \
        vim=2:9.1.0016-1ubuntu7.20 \
        # archives and dev
        bc=1.07.1-3ubuntu4 \
        make=4.3-4.1build2 \
        rsync=3.2.7-1ubuntu1.5 \
        shellcheck=0.9.0-1 \
        unzip=6.0-28ubuntu4.1 \
        xz-utils=5.6.1+really5.4.5-1ubuntu0.3 \
        zip=3.0-13ubuntu0.2 \
        # terminal and processes
        htop=3.3.0-4build1 \
        procps=2:4.0.4-4ubuntu3.3 \
        tmux=3.4-1ubuntu0.1 \
    && ln -s /usr/bin/fdfind /usr/local/bin/fd \
    && ln -s /usr/bin/batcat /usr/local/bin/bat \
    && rm -rf /var/lib/apt/lists/*

# Upstream tools, verified in the fetch stage. Kept after the apt layer so
# bumping KUBECTL_VERSION or AWS_CLI_VERSION doesn't invalidate it.
COPY --from=fetch /out/kubectl /usr/local/bin/kubectl
COPY --from=fetch /usr/local/aws-cli /usr/local/aws-cli
RUN ln -s /usr/local/aws-cli/v2/current/bin/aws /usr/local/bin/aws \
    && ln -s /usr/local/aws-cli/v2/current/bin/aws_completer /usr/local/bin/aws_completer

RUN userdel --remove ubuntu 2>/dev/null; \
    useradd --create-home --uid 1000 tingle
USER tingle
