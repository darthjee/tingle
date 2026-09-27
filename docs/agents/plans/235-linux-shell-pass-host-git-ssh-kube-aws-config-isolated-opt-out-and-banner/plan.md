# Plan: linux shell: pass host git/ssh/kube/aws config, --isolated opt-out and banner

Issue: [235-linux-shell-pass-host-git-ssh-kube-aws-config-isolated-opt-out-and-banner.md](../../issues/235-linux-shell-pass-host-git-ssh-kube-aws-config-isolated-opt-out-and-banner.md)

## Overview
`tingle linux shell` gains host integration. It conditionally mounts git and ssh config, the SSH agent socket, the kubeconfig and `~/.aws`, and forwards non-empty `AWS_*` variables. It also resets git's credential helper and, on native Linux Docker only, uses `--network host`. All of this goes through part 2's `docker_run` extra-args contract. `--isolated` or `TINGLE_LINUX_ISOLATED=1` turns it all off, and a one-line stderr banner reports the image version. The image pre-creates `~/.kube` and `~/.config` so these mounts don't create root-owned parent directories. That changes the image, so `VERSION` goes to `0.0.3`.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Flag / env:** `tingle linux shell --isolated`, or `TINGLE_LINUX_ISOLATED=1` (exactly `1`; any other value, or unset, means not isolated). `--isolated` is the only option `shell` accepts. Any other argument is an error: print `tingle linux shell: unknown option '<arg>'` to stderr and exit 1.
- **Banner** (stderr, `shell` only, printed before `docker run`):
  `tingle linux <VERSION> — <tool list> (full list: docs/guides/linux.md)`, with ` (isolated)` appended when isolated. The version is read from `shell/linux/VERSION` (`0.0.3` after this issue). The tool list is a constant in `shell/linux/executor.sh`, kept in sync with the Dockerfile by hand.
- **Container paths:** `/home/tingle/.gitconfig`, `/home/tingle/.config/git/`, `/home/tingle/.ssh/known_hosts`, `/home/tingle/.ssh/host_config`, `/home/tingle/.kube/config` (with `KUBECONFIG` set to that path), `/home/tingle/.aws/`. The SSH agent socket is `/run/host-services/ssh-auth.sock` under Docker Desktop, or the same path as `$SSH_AUTH_SOCK` on native Linux, with `SSH_AUTH_SOCK` set to it.
- **Image:** `/home/tingle/.kube` and `/home/tingle/.config` exist with mode 1777, next to `/home/tingle/.ssh`.
- **Forwarded env names:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION` (each only when non-empty, passed as `-e NAME` without a value), plus `GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=credential.helper`, `GIT_CONFIG_VALUE_0=` (empty).
- **Completion:** after `tingle linux shell`, completion offers `--isolated`.
