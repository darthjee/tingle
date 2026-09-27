# `tingle-linux` Docker image

This is the implementation view of the image. For the user-facing view
(prerequisites, what's inside the shell, host integration and `--isolated`),
see the user guide [`docs/guides/linux.md`](../guides/linux.md), in
particular [What's inside the shell](../guides/linux.md#whats-inside-the-shell).

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
  image ends with `USER tingle`, uid 1000, with
  `ENTRYPOINT ["/usr/local/bin/tingle-entrypoint"]` and `CMD ["bash"]`; see
  [Entrypoint, identity and hardening](#entrypoint-identity-and-hardening))
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
  - identity: `libnss-wrapper`, used by the entrypoint to give a foreign
    uid a passwd/group entry;
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
  read this file instead of hardcoding a tag. It is bumped together with
  the other release version references by `scripts/bump-version.sh`, never
  by hand on its own (see [Bumping versions](#bumping-versions)).
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
     every tool in the toolbox (the `TOOL_CHECKS` array, one per tool plus
     the CA bundle). The tool checks run as the `tingle` user in a single
     `--network none` container per platform, so they prove each tool works
     without network access. It also runs the identity and hardening checks
     (`smoke_test_identity`, also `--network none`, grouped into as few
     containers as possible because QEMU runs are slow):
     - default command: the image config has
       `Entrypoint == ["/usr/local/bin/tingle-entrypoint"]` and
       `Cmd == ["bash"]`, and `echo 'echo ok' | docker run --rm -i <image>`
       prints exactly `ok` (no TTY needed in CI);
     - foreign uid (`--user 501:20`): `id -un` is `tingle-host`, `$HOME` is
       `/home/tingle`, `$HOME`, `$HOME/.ssh`, `$HOME/.kube` and
       `$HOME/.config` are writable (the last two are the parents of the
       `shell` host-integration mounts),
       `ssh -G localhost` succeeds, and `/etc/passwd` is still root-owned,
       not writable and has the same sha256 as in a default-uid run;
     - default uid: `id -un` is `tingle` and `LD_PRELOAD` is empty, so
       `nss_wrapper` isn't used;
     - stdin and exit codes: `printf a | docker run --rm -i <image> sed s/a/b/`
       prints exactly `b` (proving the entrypoint adds no output), and
       `docker run --rm <image> false` exits non-zero;
     - no setuid/setgid: `find / -xdev -perm /6000 -type f` prints nothing.

     It fails if any platform fails.
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
- **`docker_run`**: `shell/linux/docker_run.sh` defines
  `docker_run <mode> [docker-args...] -- <command> [args...]`, where
  `<mode>` is `none`, `tty` or `stdin`. Handlers put extra `docker run`
  arguments (for example volume mounts) before `--`, and the command after
  it. The `--` is required, so a `--` among the command's own arguments
  (for example `tingle linux sed -- ...`) is never mistaken for the
  separator. Every run gets `--user "$(id -u):$(id -g)"` and
  `--security-opt no-new-privileges`. `tingle linux shell` uses this
  extra-args slot for its host integration (see
  [`shell` host integration](#shell-host-integration)); `tingle linux sed`
  stays a bare `docker_run stdin -- sed ...` with no extra args.

## Entrypoint, identity and hardening

- **Why a foreign uid**: `docker_run` runs every container with the host
  uid and gid (`--user "$(id -u):$(id -g)"`), so files written through a
  bind mount are owned by the host user. On macOS that is typically
  `501:20`, which doesn't exist in the image (its only user is `tingle`,
  uid 1000). Without an identity, `HOME` is `/` and not writable (breaking
  `git`, bash history and the `kubectl`/`aws` caches), and `ssh` aborts
  with `No user exists for uid 501`.
- **Entrypoint**: `shell/linux/entrypoint.sh`, installed as
  `/usr/local/bin/tingle-entrypoint` (mode 0755). With no command,
  `CMD ["bash"]` applies, so `docker run -it darthjee/tingle:<tag>` still
  opens `bash` (setting `ENTRYPOINT` would otherwise clear the `CMD`
  inherited from `ubuntu`). The entrypoint:
  - always exports `HOME=/home/tingle`;
  - when `id -un` fails (the uid has no passwd entry), finds
    `libnss_wrapper.so` under `/usr/lib/*/` at runtime (so the same script
    works on amd64 and arm64), copies `/etc/passwd` and `/etc/group` into a
    `mktemp -d` directory, appends
    `tingle-host:x:<uid>:<gid>::/home/tingle:/bin/bash` to the passwd copy,
    appends `tingle-host:x:<gid>:` to the group copy only when the gid has
    no group yet (on Ubuntu gid 20 is already `dialout`), and exports
    `LD_PRELOAD`, `NSS_WRAPPER_PASSWD` and `NSS_WRAPPER_GROUP`. `id -un`
    then prints `tingle-host`;
  - with the default uid 1000, sets none of those variables;
  - skips the identity step, without failing, when the library or a
    temporary directory is unavailable;
  - writes nothing to stdout, and nothing to stderr on success, and always
    ends with `exec "$@"`, so pipelines, stdin handling and exit codes of
    commands such as `tingle linux sed` are unchanged.
- **Why not a writable `/etc/passwd`**: it would fix identity too, but it
  lets any process in the container add a uid-0 entry, `su` to root, and
  then write root-owned files into mounted host directories. `nss_wrapper`
  keeps `/etc/passwd` and `/etc/group` read-only and unmodified; only the
  per-container copies in the temporary directory change.
- **Writable `HOME`, `~/.ssh`, `~/.kube` and `~/.config`**:
  `/home/tingle`, `/home/tingle/.ssh`, `/home/tingle/.kube` and
  `/home/tingle/.config` are mode 1777 (world-writable with the sticky
  bit), so any uid can write there. The three subdirectories are created in
  the image because they are the parents of the `shell` host-integration
  bind mounts (`~/.ssh/known_hosts` and `~/.ssh/host_config`,
  `~/.kube/config`, `~/.config/git`). When a bind mount targets a path
  whose parent doesn't exist, Docker creates that parent as root, and
  then neither the entrypoint nor the tools could write there (the
  generated `~/.ssh/config`, `ssh`'s `known_hosts` updates, kubectl's
  `~/.kube/config.lock` and caches, other tools' `~/.config/*`). `ssh`
  still accepts the generated config, because it only checks the config
  file itself, which the running uid writes as 0644.
- **No privilege escalation**: the Dockerfile strips every setuid and
  setgid bit (`find / -xdev -perm /6000 -type f -exec chmod a-s {} +`), so
  `find / -xdev -perm /6000 -type f` returns nothing, and `docker_run`
  always passes `--security-opt no-new-privileges`.
- **`~/.ssh/host_config` contract (#235)**: the handler that shares the
  host ssh setup mounts the host `~/.ssh/config` at
  `/home/tingle/.ssh/host_config`. When that file exists and
  `~/.ssh/config` does not, the entrypoint writes `~/.ssh/config` containing
  exactly:

  ```text
  IgnoreUnknown UseKeychain,AddKeysToAgent
  Include ~/.ssh/host_config
  ```

  so Linux `ssh` ignores macOS-only options such as `UseKeychain`, which it
  would otherwise reject. An existing `~/.ssh/config` is never overwritten.
  Ownership (checked for #235 on Docker Desktop for macOS): the mounted
  `host_config` shows the host uid as its owner, which is the uid `ssh`
  runs as, and `ssh` accepts it at mode 644 and 664, so including it in
  place works. Not checked on native Linux Docker, where it is expected
  to behave the same (the bind mount keeps the host uid, which is also the
  container uid).

## `shell` host integration

`tingle linux shell [--isolated]` (issue #235) brings the host's git, ssh,
kube and aws configuration into the container, so the toolbox works against
the user's real repos, clusters and accounts. The handler
(`_handle_shell` / `_shell_args` in `shell/linux/executor.sh`) builds a
list of extra `docker run` args and passes them through `docker_run`'s
extra-args contract: `docker_run tty <args...> -- bash`. Each item is added
only when it applies (the host file or directory exists, the variable is
non-empty, ...) and is silently skipped otherwise.

| Area | Host source | Container | Mode / notes |
| --- | --- | --- | --- |
| git | `~/.gitconfig` (file) | `/home/tingle/.gitconfig` | read-only |
| git | `~/.config/git/` (directory) | `/home/tingle/.config/git/` | read-only |
| git | always | `-e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=credential.helper -e GIT_CONFIG_VALUE_0=` | resets the credential helper (see below) |
| ssh | agent socket (see the rule below) | `/run/host-services/ssh-auth.sock`, or the same path as `$SSH_AUTH_SOCK` | `SSH_AUTH_SOCK` set to the container path |
| ssh | `~/.ssh/known_hosts` (file) | `/home/tingle/.ssh/known_hosts` | read-only |
| ssh | `~/.ssh/config` (file) | `/home/tingle/.ssh/host_config` | read-only, included by the entrypoint (see [`~/.ssh/host_config` contract](#entrypoint-identity-and-hardening)) |
| kube | first existing file in `${KUBECONFIG:-~/.kube/config}` | `/home/tingle/.kube/config` | read-write, `KUBECONFIG=/home/tingle/.kube/config` |
| aws | `~/.aws/` (directory) | `/home/tingle/.aws/` | read-write (SSO and CLI caches) |
| aws | non-empty `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION` | same names | passed as `-e NAME` without a value, so values never appear on the `docker run` command line |
| network | native Docker on a Linux host only | `--network host` | clusters and services on the host's `127.0.0.1` are reachable |

- **Never mounted**: private keys and the `~/.ssh` directory itself. Only
  `known_hosts` and `config` are mounted, and authentication goes through
  the agent.
- **Kubeconfig**: `$KUBECONFIG` is split on `:` by hand (no word
  splitting, so paths with spaces or glob characters are safe), and only
  the first entry that is an existing file is mounted, as a single file.
  Kubeconfig merging across several files is not supported.
- **SSH agent rule**:
  - Docker Desktop (detected by `docker info --format
    '{{.OperatingSystem}}'` containing `Docker Desktop`, on any host OS):
    mount `/run/host-services/ssh-auth.sock` at the same path, set
    `SSH_AUTH_SOCK` to it, and add `--group-add 0`. The socket only exists
    inside the Docker Desktop VM, so it isn't checked on the host. A failing
    `docker info` counts as "not Docker Desktop".
  - Native Docker on a Linux host (`uname -s` is `Linux` and not Docker
    Desktop), when `$SSH_AUTH_SOCK` is a socket (`-S`): mount it at the
    same path and set `SSH_AUTH_SOCK` to it.
  - Otherwise (for example macOS without Docker Desktop, or no agent): no
    agent is passed.
- **`--group-add 0` (Docker Desktop only)**: inside the container, Docker
  Desktop's socket is `root:root` with mode 660, so the non-root host uid
  got `Permission denied`. The supplementary root group gives it access.
  This is acceptable because the only root-group-writable paths in the
  image are already mode 1777 (`~/.ssh`, `~/.kube`, `~/.config`, `/tmp`,
  `/var/tmp`, `/run/lock`), there are no setuid/setgid files,
  `no-new-privileges` still applies, and new files keep the primary gid.
- **Credential-helper reset**: the host `~/.gitconfig` often sets
  `credential.helper` (for example `osxkeychain` on macOS), which doesn't
  exist in the image. `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/
  `GIT_CONFIG_VALUE_0` set `credential.helper` to an empty value, which
  clears the helper list, so git doesn't try to run it.
- **`--network host`**: only on native Docker on a Linux host, where the
  container then shares the host network (local clusters on `127.0.0.1`,
  VPN routes). It is never used under Docker Desktop, where host
  networking refers to the VM.
- **Opt-out**: `tingle linux shell --isolated`, or `TINGLE_LINUX_ISOLATED=1`
  (exactly `1`; any other value, or unset, means not isolated), skips all
  of the above, including the `docker info` detection, and runs a bare
  `docker_run tty -- bash`. `--isolated` is the only option `shell`
  accepts. Any other argument prints
  `tingle linux shell: unknown option '<arg>'` to stderr and exits 1.
  Completion offers `--isolated` after `tingle linux shell` (unless it is
  already typed), from `shell/linux/completion.sh`, without starting
  Docker.
- **Banner**: before `docker run`, `shell` (never `sed`) prints one line to
  stderr:
  `tingle linux <VERSION> — <tool list> (full list: docs/guides/linux.md)`,
  with ` (isolated)` appended when isolated. `<VERSION>` is read from
  `shell/linux/VERSION` (`0.1.0` since #236, the first released version
  with the toolbox and the host integration). The tool list is the
  `LINUX_TOOLS` constant in `shell/linux/executor.sh`
  (`git, ssh, jq, curl, wget, vim, rg, fd, bat, tmux, make, kubectl, aws, ...`),
  kept in sync with the Dockerfile by hand (see
  [Bumping versions](#bumping-versions)).
- **Implementation-time checks (#235)**:
  - kubectl with a single-file kubeconfig bind mount (Docker Desktop for
    macOS): `kubectl config use-context` and `set-context` write the file
    in place (same inode), and the change persists to the host. So only
    the file is mounted, not `~/.kube`.
  - ssh `host_config` ownership (Docker Desktop for macOS): see the
    [`~/.ssh/host_config` contract](#entrypoint-identity-and-hardening).
  - Docker Desktop agent socket for a non-root uid: `Permission denied`
    without a group, which led to `--group-add 0`. With it, connecting to
    the socket works. Listing real keys (`ssh-add -l` with keys loaded)
    was not verified.
- **Known limitations**:
  - Native Linux Docker is not verified end to end: `--network host` and
    the `$SSH_AUTH_SOCK` mount are only covered by stubbed tests.
  - `aws sts get-caller-identity` through the mounted `~/.aws` and the
    forwarded variables is not verified.
  - Only the first existing kubeconfig file is mounted (no merging).
  - The read-write `~/.kube/config` and `~/.aws/` mounts mean changes made
    in the container (context switches, SSO logins, caches) change the
    host files. Use `--isolated` to avoid that.
  - The banner's tool list is hardcoded and can drift from the Dockerfile.

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
4. If a tool is added or removed, update every tool list by hand (nothing
   checks that they agree):
   - the Dockerfile header;
   - the toolbox groups in this doc;
   - the `TOOL_CHECKS` array in `scripts/release_image.sh`;
   - for a main tool, the `LINUX_TOOLS` banner constant in
     `shell/linux/executor.sh`;
   - the user guide's
     [What's inside the shell](../guides/linux.md#whats-inside-the-shell)
     section;
   - `DOCKERHUB_DESCRIPTION.md` (and `DOCKERHUB_SHORT_DESCRIPTION.txt` if
     it names the tool).
5. Bump the release version with `scripts/bump-version.sh X.Y.Z` and
   release as usual (push git tag `X.Y.Z`).

The release version lives in three places that must stay in sync: the
README "Current Version" / "Next Release" lines, the `TINGLE_VERSION`
default in `install/bootstrap.sh`, and `shell/linux/VERSION`.
`scripts/bump-version.sh` updates all three, so don't hand-edit `VERSION`
alone. #235 did that (`0.0.3`), which left the three out of sync and
`0.0.3` never tagged; #236 resynced them at `0.1.0`. A git tag `X.Y.Z`
triggers both the image release (`build-and-publish-linux-image`,
`update-description`) and the CLI release zip (`build-and-publish-release`).
