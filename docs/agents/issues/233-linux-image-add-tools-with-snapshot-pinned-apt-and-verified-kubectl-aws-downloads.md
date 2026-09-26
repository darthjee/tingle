# Issue: linux image: add tools with snapshot-pinned apt and verified kubectl/aws downloads

## Description
Part 1 of #231. Add the new tools to the `darthjee/tingle` image (`shell/linux/Dockerfile`), with reproducible pins, and cover them in the release smoke test and a report-only CVE scan. The image currently ships only a baseline GNU toolbox (`coreutils`, `findutils`, `grep`, `sed`, `gawk`, `tar`, `diffutils`).

The multi-architecture build (#232) has already landed: `scripts/release_image.sh` builds one local image per platform in `$PLATFORMS` (`darthjee/tingle:<tag>-amd64`, `darthjee/tingle:<tag>-arm64`). Everything below must work on both platforms.

## Problem
The shell opened by `tingle linux shell` lacks everyday tools. The existing exact apt pins, required by Codacy's Hadolint DL3008 (#67), break the build whenever Ubuntu supersedes a pinned version, because `noble-updates` and `noble-security` keep only the latest version. Adding about 28 more packages would make that frequent.

## Expected Behavior
- **apt packages** (Ubuntu 24.04, each pinned to an exact version):
  - git and friends: `git`, `ca-certificates`, `openssh-client`, `less`;
  - data and network: `jq`, `curl`, `wget`, `dnsutils`, `iputils-ping`, `netcat-openbsd`, `iproute2`;
  - editing, search and viewing: `vim`, `ripgrep`, `fd-find`, `bat`, `bash-completion`, `tree`, `file`;
  - archives and dev: `unzip`, `zip`, `xz-utils`, `bc`, `make`, `shellcheck`, `rsync`;
  - terminal and processes: `procps`, `tmux`, `htop`.
- `fd` and `bat` are available under those names, as symlinks in `/usr/local/bin` to Ubuntu's `fdfind` and `batcat`.
- **Upstream tools**, not from apt: `kubectl` and AWS CLI v2, in `/usr/local/bin`, runnable by the non-root user, on both `amd64` and `arm64`.
- `gnupg`, the downloaded installers and any extracted installer files are not in the final image.
- A build from the same Dockerfile always installs the same versions and never fails because a version was removed upstream.
- The existing `tingle linux sed` behaviour is unchanged.
- `scripts/release_image.sh scan` prints a Trivy vulnerability report for each per-platform image and always exits 0.

## Solution
- **Base image:** pin it by digest: `FROM ubuntu:24.04@sha256:<digest>`. Use the multi-platform index digest, so both architectures resolve.
- **apt:**
  - `ARG UBUNTU_SNAPSHOT=<YYYYMMDDTHHMMSSZ>`, then `apt-get update --snapshot "$UBUNTU_SNAPSHOT"` (Ubuntu snapshot service, native on 24.04).
  - Resolve every pin, including the 7 existing ones, against that date. Check that each pinned version exists for both `amd64` and `arm64` (the ports archive).
  - Check that `--snapshot` works before `ca-certificates` is installed; if it doesn't, install `ca-certificates` first.
- **Multi-stage build for the upstream tools:**
  - A `fetch` builder stage (same pinned base and snapshot) installs its own pinned `curl`, `ca-certificates`, `unzip` and `gnupg`, downloads and verifies both tools, and installs the AWS CLI into `/usr/local/aws-cli`.
  - The final stage uses `COPY --from=fetch` to copy `kubectl` into `/usr/local/bin` and `/usr/local/aws-cli` across, then recreates the `aws` / `aws_completer` symlinks in `/usr/local/bin`. `gnupg` and the installer files never reach the final image.
- **kubectl:** `ARG KUBECTL_VERSION`. Download `https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/<arch>/kubectl` and verify it against the published `kubectl.sha256` (`sha256sum --check`).
- **AWS CLI v2:** `ARG AWS_CLI_VERSION`. Download `awscli-exe-linux-<arch>-${AWS_CLI_VERSION}.zip` and its `.sig`, and verify them with AWS's PGP public key. Store the key in the repo (for example `shell/linux/aws-cli.asc`, fingerprint noted in a comment) instead of fetching it at build time.
- Any failed verification fails the build.
- **Architecture:** pick downloads from `TARGETARCH` / `dpkg --print-architecture` (`amd64` → `x86_64` and `arm64` → `aarch64` for the AWS CLI). Never hard-code `amd64`.
- **Install location:** install the upstream tools as root, before `USER tingle`.
- **Layers:** order them base → apt → upstream tools. Clean the apt lists in the same `RUN`.
- **Hadolint:** use `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` for `RUN`s with pipes, and `curl -fsSL`, so Hadolint (DL4006, DL3047, DL3008) stays clean in both stages.
- **Header comment:** update the Dockerfile header comment for the new toolbox.
- **Smoke test (`smoke_test_image` in `scripts/release_image.sh`, run for each platform):**
  - Run each tool's `--version` (or a no-op), including `fd`, `bat`, `kubectl version --client` and `aws --version`. Fail on the first missing tool, naming it.
  - Check that `/etc/ssl/certs/ca-certificates.crt` exists.
  - No network access. Keep the existing GNU `sed` and non-root checks.
- **CVE scan:**
  - Add a `scan` subcommand to `scripts/release_image.sh`. It runs a pinned `aquasec/trivy` image against each per-platform local image (`<tag>-<arch>`), prints the findings, and always exits 0, even when Trivy itself fails.
  - It skips when `shell/linux/` hasn't changed since the previous tag, like `build` and `smoke-test`.
  - Add it to the usage line and the header comment. Add a `Scan image` step to the CircleCI `build-and-publish-linux-image` job, between `Smoke test` and `Publish image`.
- **Docs:** update `docs/agents/tingle-linux-image.md` with the toolbox groups, the snapshot and pinning approach, the builder stage, the `scan` step, and the manual bump procedure:
  1. Pick a new snapshot date and base digest.
  2. Re-resolve the pins (`apt-cache policy` after `apt-get update --snapshot`) for both architectures.
  3. Bump `KUBECTL_VERSION` and `AWS_CLI_VERSION`, and rotate the AWS key if needed.
  4. Update the tool lists in the docs.
  5. Bump `VERSION`.
- **Out of scope:**
  - Do **not** bump `shell/linux/VERSION` here; #236 does the release.
  - The user-facing docs (`docs/guides/linux.md`, `DOCKERHUB_DESCRIPTION.md`, `DOCKERHUB_SHORT_DESCRIPTION.txt`) also land in #236.
  - The entrypoint, `libnss-wrapper` and hardening belong to #234.
  - Passing host config into the container belongs to #235.

## Benefits
- A useful shell toolbox, including `kubectl` and `aws` for the `tingle kube` workflow.
- Reproducible builds that don't break when Ubuntu updates packages.
- A verified supply chain for the non-apt downloads, with no build-only tools left in the image.
- Visibility into the CVEs that build up on frozen pins, without blocking releases.
