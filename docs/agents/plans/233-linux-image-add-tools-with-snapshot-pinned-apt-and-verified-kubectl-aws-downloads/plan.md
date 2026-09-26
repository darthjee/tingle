# Plan: linux image: add tools with snapshot-pinned apt and verified kubectl/aws downloads

Issue: [233-linux-image-add-tools-with-snapshot-pinned-apt-and-verified-kubectl-aws-downloads.md](../../issues/233-linux-image-add-tools-with-snapshot-pinned-apt-and-verified-kubectl-aws-downloads.md)

## Overview
Grow the `darthjee/tingle` image from the baseline GNU toolbox into a general shell toolbox. That means about 28 more apt packages, the `fd`/`bat` symlinks, and `kubectl` plus AWS CLI v2 from upstream.

Everything is reproducible: the base image is pinned by digest, apt is pinned against a fixed Ubuntu snapshot date, and the upstream downloads are verified in a `fetch` builder stage, so `gnupg` never reaches the final image. The release script's smoke test covers every tool on each platform. A new report-only `scan` subcommand runs Trivy and gets its own CircleCI step. The agent doc explains the approach and the manual bump procedure.

## Agents involved

- [shell](shell.md) — `shell/linux/Dockerfile` and the AWS CLI public key.
- [architect](architect.md) — root-level `scripts/release_image.sh` and `.circleci/config.yml` (smoke test, `scan`, CI step). The parent issue #231 assigns this part to the architect because the files are root-level.
- [product-owner](product-owner.md) — `docs/agents/tingle-linux-image.md`.

## Shared contracts

### Build context
`scripts/release_image.sh` builds with `-f shell/linux/Dockerfile .`, so the **build context is the repo root**. Every `COPY` source in the Dockerfile is repo-relative, for example `COPY shell/linux/aws-cli.asc /tmp/aws-cli.asc`. Do not change the build invocation.

### Dockerfile interface (produced by shell; documented by product-owner)
| Item | Value |
|---|---|
| Base | `ubuntu:24.04@sha256:<multi-platform index digest>` — used by both stages |
| Stages | `fetch` (builder; downloads and verifies upstream tools) → final unnamed stage |
| `ARG UBUNTU_SNAPSHOT` | `YYYYMMDDTHHMMSSZ` — the snapshot date that every apt pin resolves against, in both stages |
| `ARG KUBECTL_VERSION` | e.g. `1.31.x`, without the `v` prefix |
| `ARG AWS_CLI_VERSION` | e.g. `2.x.y` |
| `ARG TARGETARCH` | declared in `fetch`; `amd64` or `arm64` (supplied by buildx) |
| AWS key file | `shell/linux/aws-cli.asc`, with the fingerprint in a Dockerfile comment |

### Installed paths in the final image (produced by shell; consumed by architect's smoke test)
- `/usr/local/bin/kubectl` (mode 0755)
- `/usr/local/aws-cli/` (copied from `fetch`), with `/usr/local/bin/aws` and `/usr/local/bin/aws_completer` symlinked into `/usr/local/aws-cli/v2/current/bin/`
- `/usr/local/bin/fd` → `/usr/bin/fdfind`, and `/usr/local/bin/bat` → `/usr/bin/batcat`
- `/etc/ssl/certs/ca-certificates.crt` (from `ca-certificates`)
- The image still ends with `USER tingle` (uid 1000) and still has no `CMD`/`ENTRYPOINT`.

### Smoke-check table (shell's package list ↔ architect's smoke test)
The check commands the architect's smoke test runs. The shell agent must make every one of them succeed as the `tingle` user with no network access:

| Tool | Check |
|---|---|
| git | `git --version` |
| ssh | `ssh -V` |
| less | `less --version` |
| jq | `jq --version` |
| curl | `curl --version` |
| wget | `wget --version` |
| dig | `dig -v` |
| ping | `ping -V` |
| nc | `command -v nc` (openbsd `nc` has no clean version flag) |
| ip | `ip -V` |
| vim | `vim --version` |
| rg | `rg --version` |
| fd | `fd --version` |
| bat | `bat --version` |
| bash-completion | `test -f /usr/share/bash-completion/bash_completion` |
| tree | `tree --version` |
| file | `file --version` |
| unzip | `unzip -v` |
| zip | `zip -v` |
| xz | `xz --version` |
| bc | `bc --version` |
| make | `make --version` |
| shellcheck | `shellcheck --version` |
| rsync | `rsync --version` |
| ps | `ps --version` |
| tmux | `tmux -V` |
| htop | `htop --version` |
| kubectl | `kubectl version --client` |
| aws | `aws --version` |
| ca bundle | `test -s /etc/ssl/certs/ca-certificates.crt` |

If the shell agent finds that a check command doesn't work as written on Ubuntu 24.04, it must swap in an equivalent no-op and tell the architect.

### Release script interface (produced by architect; documented by product-owner)
- New subcommand `scripts/release_image.sh scan`. It scans each `darthjee/tingle:<tag>-<arch>` for the platforms in `$PLATFORMS`, with a pinned `aquasec/trivy:<version>` image, prints the report and always exits 0. It skips when `shell/linux/` is unchanged since the previous tag.
- New CircleCI step `Scan image` in `build-and-publish-linux-image`, between `Smoke test` and `Publish image`.

## Notes
- The recommended order is shell first, because the smoke test depends on the installed paths. The architect's changes can be written in parallel against the contract above. The product-owner goes last, so it documents the final values.
- `shell/linux/VERSION` is **not** bumped here; #236 handles the release. Because nothing is tagged, merging this doesn't publish anything.
