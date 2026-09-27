# tingle

The GNU/Linux toolbox image behind the `tingle linux` command of
[tingle](https://github.com/darthjee/tingle). It gives `tingle linux`
subcommands (`shell`, `sed`, ...) consistent GNU behavior, independent of
the BSD userland shipped with macOS, and makes `tingle linux shell` a ready
Linux workstation (git, jq, kubectl, aws CLI, ...).

Supported platforms: `linux/amd64`, `linux/arm64`.

## What it contains

Built on `ubuntu:24.04`, with these tools:

- **GNU baseline**: coreutils, findutils, `grep`, GNU `sed`, `gawk`, `tar`,
  diffutils (`diff`, `cmp`)
- **git & ssh**: `git`, `ssh` / `scp` / `ssh-add` / `ssh-keygen`
  (openssh-client)
- **data & network**: `jq`, `curl`, `wget`, `dig` (dnsutils), `ping`
  (iputils-ping), `nc` (netcat-openbsd), `ip` (iproute2)
- **search & viewing**: `rg` (ripgrep), `fd` (fd-find), `bat`, `less`,
  `tree`, `file`, `vim`
- **dev & archives**: `make`, `shellcheck`, `bc`, `rsync`, `zip`, `unzip`,
  `xz` (xz-utils)
- **terminal**: `bash` with bash-completion, `tmux`, `htop`, `ps` (procps)
- **Kubernetes & AWS**: `kubectl`, `aws` (AWS CLI v2)

See
[What's inside the shell](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md#whats-inside-the-shell)
for what each tool is for.

The image runs as the non-root user `tingle` (uid 1000), so files touched
through a volume mount stay owned by your user on the host.

Every command runs through the entrypoint
`/usr/local/bin/tingle-entrypoint`, which gives an unknown uid (such as the
host uid `tingle linux` passes with `--user`) a usable identity. With no
command, the image runs `bash`.

`tingle linux shell` also brings in your host git, ssh, kube and aws
config (opt out with `--isolated`). See the
[`tingle linux` guide](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md)
for details and security notes.

## Usage

### Through `tingle linux` (preferred)

Install [tingle](https://github.com/darthjee/tingle) and run:

```bash
tingle linux sed --version
tingle linux shell
```

See the
[`tingle linux` guide](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md)
for all subcommands and options.

### Directly with Docker

```bash
docker run --rm -v "$PWD:$PWD" -w "$PWD" darthjee/tingle:<tag> <cmd> [args...]
```

For example:

```bash
docker run --rm -v "$PWD:$PWD" -w "$PWD" darthjee/tingle:<tag> sed --version
```

## Tags

- Tags are plain semver (for example `1.0.0`), the same string as the
  matching `X.Y.Z` git tag.
- Images are built and published by CircleCI when that git tag is pushed.
- The current tag is pinned in
  [`shell/linux/VERSION`](https://github.com/darthjee/tingle/blob/main/shell/linux/VERSION).

## Links

- [Repository](https://github.com/darthjee/tingle)
- [`tingle linux` guide](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md)
- [Dockerfile](https://github.com/darthjee/tingle/blob/main/shell/linux/Dockerfile)
