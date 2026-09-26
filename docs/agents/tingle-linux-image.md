# `tingle-linux` Docker image

- **Image**: `darthjee/tingle` on Docker Hub.
- **Tag strategy**: the published Docker tag is exactly the plain semver
  git tag — pushing git tag `1.0.0` publishes `darthjee/tingle:1.0.0`
  (same string, not two different formats). The git tag is pushed by hand;
  CircleCI then builds and publishes the image. There is no `latest` tag and
  no build on regular commits. A `v`-prefixed tag triggers no release
  (silently ignored by the CircleCI tag filter). Each published tag is one
  multi-platform manifest covering `linux/amd64` and `linux/arm64`. No
  per-architecture tags (e.g. `1.0.0-arm64`) are published.
- **Source**: `shell/linux/Dockerfile` — a non-root `ubuntu` base (the
  image ends with `USER tingle`, uid 1000, and sets no `CMD`/`ENTRYPOINT`)
  with a general shell toolbox. The build context is the repo root
  (`docker buildx build -f shell/linux/Dockerfile .`), so every `COPY`
  source is repo-relative. The toolbox groups (kept in sync with the
  Dockerfile header):
  - GNU baseline: `coreutils`, `findutils`, `grep`, GNU `sed`, `gawk`,
    `tar`, `diffutils`;
  - git and friends: `git`, `ca-certificates`, `openssh-client`, `less`;
  - data and network: `jq`, `curl`, `wget`, `dig` (`dnsutils`), `ping`
    (`iputils-ping`), `nc` (`netcat-openbsd`), `ip` (`iproute2`);
  - editing, search and viewing: `vim`, `rg` (`ripgrep`), `fd` (`fd-find`),
    `bat`, `bash-completion`, `tree`, `file`. Ubuntu ships `fd` as `fdfind`
    and `bat` as `batcat`, so the image adds the symlinks
    `/usr/local/bin/fd` -> `/usr/bin/fdfind` and `/usr/local/bin/bat` ->
    `/usr/bin/batcat`;
  - archives and dev: `unzip`, `zip`, `xz` (`xz-utils`), `bc`, `make`,
    `shellcheck`, `rsync`;
  - terminal and processes: `ps` (`procps`), `tmux`, `htop`;
  - from upstream: `kubectl` (`/usr/local/bin/kubectl`) and the AWS CLI v2
    (installed in `/usr/local/aws-cli/`, with `/usr/local/bin/aws` and
    `/usr/local/bin/aws_completer` symlinked into
    `/usr/local/aws-cli/v2/current/bin/`).
- **Reproducible pins**: the same Dockerfile builds the same image later.
  - The base is pinned by its multi-platform index digest in a top-level
    `ARG BASE_IMAGE`
    (`ubuntu:24.04@sha256:008173c23f95b170204355c12626cb5a965d779a7e1283b09e9cffbb1bf33ca3`),
    which both stages build on and which resolves on `linux/amd64` and
    `linux/arm64`.
  - Every apt package is pinned to an exact version, resolved against a
    fixed Ubuntu snapshot: the top-level `ARG UBUNTU_SNAPSHOT`
    (`YYYYMMDDTHHMMSSZ`, currently `20260920T000000Z`) is passed to
    `apt-get update --snapshot` and `apt-get install --snapshot`, served by
    `snapshot.ubuntu.com`. Why: plain version pins (hadolint DL3008, issue
    #67) break over time, because `noble-updates`/`noble-security` drop a
    version as soon as it is superseded. A snapshot keeps serving the
    pinned versions.
  - Both stages first install `ca-certificates` from the live archive,
    because `snapshot.ubuntu.com` is HTTPS-only and the stock sources are
    plain HTTP. Without a CA bundle, `apt-get update --snapshot` only warns
    and silently keeps the live archive. They then reinstall
    `ca-certificates`, `openssl` and `libssl3t64` at the snapshot versions
    with `--allow-downgrades`, so the image only carries snapshot
    versions. `--error-on=any` turns any fetch warning into a failed
    build.
  - **Dual-architecture apt pins**: every pin must resolve on both
    architectures. amd64 uses `archive.ubuntu.com` and arm64 uses
    `ports.ubuntu.com`. apt has no built-in snapshot mapping for
    `ports.ubuntu.com`, so `/etc/apt/apt.conf.d/99snapshot-ports` points it
    at `snapshot.ubuntu.com/ubuntu`, which serves every architecture. Both
    architectures therefore resolve against the same snapshot, and a pin
    missing on either one fails the build.
- **Upstream tools**: `kubectl` and the AWS CLI v2 are downloaded and
  verified in a `fetch` builder stage. Only the verified results reach the
  final image (`/out/kubectl` and `/usr/local/aws-cli`), and they are copied
  in after the apt layer, so bumping a tool version doesn't invalidate the
  apt cache.
  - Versions: `ARG KUBECTL_VERSION` (without the `v` prefix, currently
    `1.37.1`) and `ARG AWS_CLI_VERSION` (currently `2.37.4`), both declared
    in `fetch`.
  - Architecture: `ARG TARGETARCH` (supplied by buildx, falling back to
    `dpkg --print-architecture`) picks the download. `kubectl` uses `amd64`
    and `arm64` as is. The AWS CLI maps `amd64` to `x86_64` and `arm64` to
    `aarch64`. Any other architecture fails the build.
  - `kubectl` is checked against the upstream `kubectl.sha256` with
    `sha256sum --check --strict`.
  - The AWS CLI zip is checked against its PGP signature with the in-repo
    public key `shell/linux/aws-cli.asc` (AWS CLI Team, fingerprint
    `FB5D B77F D5C1 18B8 0511 ADA8 A631 0ACC 4672 475C`, expires
    2027-07-01). `gpg` only dearmors the key. `gpgv` verifies into a
    throwaway keyring, and the build also requires a `VALIDSIG` status line
    carrying that exact fingerprint, so a swapped key file fails the build.
  - `gpg`, `curl` and `unzip` are only installed in `fetch` (pinned against
    the same snapshot), and the AWS installer and downloads are removed
    there. None of them reach the final image.
- **Version pin**: `shell/linux/VERSION` — a single line containing exactly
  the currently-published tag (e.g. `1.0.0`), the one source of truth for
  "what tag is currently published." Both CI and `shell/linux/docker_run.sh`
  read this file instead of hardcoding a tag.
- **Release script**: `scripts/release_image.sh` performs the
  build-needed check (skips rebuild/republish when `shell/linux/` hasn't
  changed since the previous release tag), build, smoke test, scan,
  publish, and `update-description` (pushes the Docker Hub description) —
  invoked from `.circleci/config.yml` rather than inlining that logic in
  the CI YAML.
  The CircleCI job `build-and-publish-linux-image` runs on a pinned
  `ubuntu-2404` machine image and calls five subcommands in order, in one
  job so the buildx cache is shared:
  1. `setup-builder` (idempotent) registers QEMU/binfmt for every
     non-native platform through a pinned `tonistiigi/binfmt` image. It
     skips this when the builder already lists every platform, as on Docker
     Desktop. It then creates and selects the `docker-container` buildx
     builder `tingle-builder`.
  2. `build` builds each platform with `--load` and tags it locally as
     `darthjee/tingle:<tag>-<arch>` (e.g. `1.0.0-amd64`, `1.0.0-arm64`).
     These tags stay in the local daemon and are never pushed.
  3. `smoke-test` runs every check against each `<tag>-<arch>` image, with
     `--platform` on every `docker run`: GNU `sed`, the non-root user, and
     every tool in the toolbox (the `TOOL_CHECKS` array, 30 checks, one per
     tool plus the CA bundle). The tool checks run as the `tingle` user in
     a single `--network none` container per platform, so they prove each
     tool works without network access. It fails if any platform fails.
  4. `scan` runs a pinned Trivy image
     (`aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969`)
     against each local `<tag>-<arch>` image, through the docker socket,
     and prints the vulnerability report. It is report-only: findings and
     Trivy failures (such as a DB download error) only print a warning, and
     it always exits 0. It runs as the CircleCI step `Scan image`, between
     `Smoke test` and `Publish image`.
  5. `publish` does one multi-platform `docker buildx build --push` of
     `darthjee/tingle:<tag>`, then runs `docker buildx imagetools inspect`
     on that tag. The job fails unless the manifest lists every platform.

  `build`, `smoke-test`, `scan` and `publish` keep the build-needed early
  exit.
  `build` and `publish` also keep the version-pin check.
- **Platforms**: the `PLATFORMS` env var (space-separated, default
  `linux/amd64 linux/arm64`) picks the platforms that `setup-builder`,
  `build`, `smoke-test`, `scan` and `publish` handle. Override it to build
  and test locally without emulation, for example `PLATFORMS=linux/arm64` on
  Apple silicon without QEMU.
- **Docker Hub description**: the short description lives in
  `DOCKERHUB_SHORT_DESCRIPTION.txt` (repo root, a single line limited to 100
  characters) and the full description lives in `DOCKERHUB_DESCRIPTION.md`
  (repo root, Markdown). `scripts/release_image.sh update-description` pushes
  both in one Docker Hub API call, through the `update-description` CircleCI
  job on release tags. It fails the job when either file is missing, the
  short description is empty or too long, or the HTTP call fails. Links in
  `DOCKERHUB_DESCRIPTION.md` must be absolute URLs, because Docker Hub cannot
  resolve paths relative to the repository.
- **Reference**: `docker run --rm darthjee/tingle:<tag> ...` — this is the
  exact image reference the `tingle linux` command's `docker run` wrapper
  should target.

## Bumping versions

Nothing bumps the pins automatically. To refresh the image by hand:

1. Pick a new `UBUNTU_SNAPSHOT` date and the current `ubuntu:24.04`
   multi-platform index digest (for example with
   `docker buildx imagetools inspect ubuntu:24.04`), and update both
   top-level `ARG`s (`UBUNTU_SNAPSHOT` and `BASE_IMAGE`).
2. Re-resolve every apt pin on both architectures (`linux/amd64` and
   `linux/arm64`), in both stages (`fetch` and the final stage): run
   `apt-get update --snapshot <date>` in the base image, then
   `apt-cache policy <package>` for each pinned package, and copy the
   candidate version into the Dockerfile. Remember the arm64
   `ports.ubuntu.com` snapshot mapping from the Dockerfile, and that
   `ca-certificates`, `openssl` and `libssl3t64` are pinned too.
3. Bump `KUBECTL_VERSION` and `AWS_CLI_VERSION`. If AWS rotated its CLI
   signing key, replace `shell/linux/aws-cli.asc` with the key from the AWS
   CLI install guide and update the fingerprint in the Dockerfile comment,
   in the `VALIDSIG` check and in this doc.
4. Update the tool lists in this doc and in the Dockerfile header (and the
   `TOOL_CHECKS` array in `scripts/release_image.sh` if a tool is added or
   removed).
5. Bump `shell/linux/VERSION` and release as usual.
