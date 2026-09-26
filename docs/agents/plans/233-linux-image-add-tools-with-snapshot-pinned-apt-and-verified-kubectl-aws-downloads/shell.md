# Shell Plan: linux image: add tools with snapshot-pinned apt and verified kubectl/aws downloads

Main plan: [plan.md](plan.md)

## Shared contracts

- **Build context is the repo root** (`-f shell/linux/Dockerfile .`), so write COPY sources as `shell/linux/...`.
- You produce the Dockerfile interface: base pinned by digest, stages `fetch` → final, `ARG`s `UBUNTU_SNAPSHOT`, `KUBECTL_VERSION`, `AWS_CLI_VERSION` and `TARGETARCH`, and key file `shell/linux/aws-cli.asc`.
- You produce these installed paths: `/usr/local/bin/{kubectl,aws,aws_completer,fd,bat}`, `/usr/local/aws-cli/`, and `/etc/ssl/certs/ca-certificates.crt`. The image still ends with `USER tingle` and has no `CMD`/`ENTRYPOINT`.
- Every command in the smoke-check table in [plan.md](plan.md#smoke-check-table-shells-package-list--architects-smoke-test) must succeed as `tingle`, with no network access, on `linux/amd64` and `linux/arm64`. If one can't, pick an equivalent and report it.

## Steps

- [01 — Pin the base image and switch apt to a snapshot](shell/01-pin-base-and-snapshot.md)
- [02 — Add the apt toolbox and fd/bat symlinks](shell/02-apt-toolbox.md)
- [03 — Add the AWS CLI public key](shell/03-aws-cli-key.md)
- [04 — Fetch stage: verified kubectl and AWS CLI](shell/04-fetch-stage.md)
- [05 — Header comment and local verification](shell/05-header-and-verify.md)

## CI Checks
- There is no CI job that builds the image on regular commits. Codacy runs Hadolint on `shell/linux/Dockerfile`, so keep DL3008 (pins), DL4006 (pipefail), DL3047 (`wget`/`curl` progress) and DL3009 (apt lists) clean. If `hadolint` is available locally, run `hadolint shell/linux/Dockerfile`.
- Local build and smoke test: `scripts/release_image.sh setup-builder && scripts/release_image.sh build && scripts/release_image.sh smoke-test`. Use `PLATFORMS=linux/arm64` or `linux/amd64` to skip emulation. Because of change detection, this only runs when `shell/linux/` changed since the previous tag.

## Notes
- Snapshot pins must exist on both `archive.ubuntu.com` (amd64) and `ports.ubuntu.com` (arm64) at that date. Resolve them with `apt-cache policy` in both architectures, using `docker run --platform linux/arm64 ...`.
- If `apt-get update --snapshot` fails over plain HTTP in the stock image, bootstrap `ca-certificates` with a normal `apt-get update` first. Still pin it to the snapshot's version, and record why in a comment.
