# Plan: linux: user docs, Docker Hub descriptions and release 0.1.0

Issue: [236-linux-user-docs-docker-hub-descriptions-and-release-0-1-0.md](../../issues/236-linux-user-docs-docker-hub-descriptions-and-release-0-1-0.md)

## Overview
Part 4 of #231. Parts 1–3 (#232–#235) are merged: the image now ships a full
toolbox (git, ssh, jq, kubectl, aws, ...), an nss_wrapper entrypoint, and
`tingle linux shell` brings in host git/ssh/kube/aws config unless
`--isolated`. This plan documents all of that for users (`docs/guides/linux.md`),
refreshes both Docker Hub descriptions, gives the agent doc a final pass, and
bumps the release version to `0.1.0` so pushing git tag `0.1.0` after merge
publishes the image, the Docker Hub description and the CLI release zip.

## Agents involved

- [architect](architect.md) — `DOCKERHUB_DESCRIPTION.md`, `DOCKERHUB_SHORT_DESCRIPTION.txt`, version bump to `0.1.0`
- [guide](guide.md) — `docs/guides/linux.md`, `docs/guides/README.md`
- [product-owner](product-owner.md) — final pass over `docs/agents/tingle-linux-image.md`

## Shared contracts

- **Grouped tool list** (single source of truth; the guide and
  `DOCKERHUB_DESCRIPTION.md` both use these seven groups, in this order, with
  these user-facing command names; package name in parentheses only where it
  differs). Verified against the final stage of `shell/linux/Dockerfile`:
  1. **GNU baseline**: coreutils, findutils, `grep`, GNU `sed`, `gawk`, `tar`, diffutils (`diff`, `cmp`)
  2. **git & ssh**: `git`, `ssh` / `scp` / `ssh-add` / `ssh-keygen` (openssh-client)
  3. **data & network**: `jq`, `curl`, `wget`, `dig` (dnsutils), `ping` (iputils-ping), `nc` (netcat-openbsd), `ip` (iproute2)
  4. **search & viewing**: `rg` (ripgrep), `fd` (fd-find), `bat`, `less`, `tree`, `file`, `vim`
  5. **dev & archives**: `make`, `shellcheck`, `bc`, `rsync`, `zip`, `unzip`, `xz` (xz-utils)
  6. **terminal**: `bash` with bash-completion, `tmux`, `htop`, `ps` (procps)
  7. **Kubernetes & AWS**: `kubectl`, `aws` (AWS CLI v2)

  Internal-only packages (`ca-certificates`, `libnss-wrapper`, `openssl`) are
  not listed as user tools.
- **Guide section anchor**: the tool list lives under the heading
  `## What's inside the shell` in `docs/guides/linux.md`, i.e.
  `https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md#whats-inside-the-shell`.
  `DOCKERHUB_DESCRIPTION.md` may link to it (absolute URL). The shell banner
  already points users to `docs/guides/linux.md` for the full list.
- **Version**: `0.1.0` everywhere (`shell/linux/VERSION`, `install/bootstrap.sh`
  default, README "Current Version"); README "Next Release" becomes `0.1.1`.
- **Short description** (exact, 93 characters):
  `GNU/Linux toolbox (GNU utils, git, jq, kubectl, aws CLI, ...) behind the tingle linux command`
- **Image pull size**: measured once by the `guide` agent (see guide.md) and
  quoted as "about N MB" in the guide's Prerequisites. Docker Hub
  description doesn't need to repeat it.

## Notes
- **Version bump scope differs from the issue text.** The issue says only
  `shell/linux/VERSION` changes. But `scripts/bump-version.sh` keeps
  `shell/linux/VERSION`, `install/bootstrap.sh` (`TINGLE_VERSION` default) and
  the README version lines in sync, and a `X.Y.Z` tag triggers both
  `build-and-publish-linux-image` and `build-and-publish-release` (CLI zip).
  #235 hand-edited only `VERSION` to `0.0.3`, so the three are currently
  out of sync (`0.0.3` vs `0.0.2`). The plan runs
  `scripts/bump-version.sh 0.1.0` instead, which fixes that and matches the
  previous bump commit (#145). Owned by `architect` because it spans root,
  `install/` and `shell/` files.
- **Release (manual, after merge):** push git tag `0.1.0` on `main`. CircleCI
  then builds, smoke-tests, scans and publishes `darthjee/tingle:0.1.0`, runs
  `update-description`, and publishes the CLI release. Not part of the PR.
- No `shell` agent work remains (its only item, the `VERSION` bump, moved to
  the architect's `bump-version.sh` run).
