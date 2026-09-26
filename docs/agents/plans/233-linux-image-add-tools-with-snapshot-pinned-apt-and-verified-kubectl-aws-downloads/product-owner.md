# Product-owner Plan: linux image: add tools with snapshot-pinned apt and verified kubectl/aws downloads

Main plan: [plan.md](plan.md)

## Shared contracts

- You document the Dockerfile interface: base digest, `fetch` stage, the `UBUNTU_SNAPSHOT`, `KUBECTL_VERSION` and `AWS_CLI_VERSION` `ARG`s, `shell/linux/aws-cli.asc`, and the installed paths.
- You document the release script interface: the `scan` subcommand and the `Scan image` CI step.
- Use the final values the shell and architect agents report, not placeholders.

## Implementation Steps

### Step 1 — Update `docs/agents/tingle-linux-image.md`
- **Source:** replace the "baseline GNU toolbox" description with the toolbox groups:
  - GNU baseline;
  - git and friends;
  - data and network;
  - editing, search and viewing (with the `fd`/`bat` symlinks);
  - archives and dev;
  - terminal and processes;
  - upstream `kubectl` and `aws`.
- **Reproducible pins** (new bullet): the digest-pinned base, apt pinned against `UBUNTU_SNAPSHOT` through `apt-get update --snapshot`, and why (#67 DL3008, where superseded versions vanish from `noble-updates`/`-security`). Fold in the existing "Dual-architecture apt pins" bullet, which now resolves against the snapshot on both archives.
- **Upstream tools** (new bullet): the `fetch` builder stage, the kubectl sha256 check, AWS CLI PGP verification with the in-repo key (`shell/linux/aws-cli.asc`, fingerprint), the architecture mapping, and that `gnupg` and the installers never reach the final image.
- **Release script:** add `scan` as a step between `smoke-test` and `publish`, running a pinned Trivy image per platform, report-only, never failing. Update "calls four subcommands" to five, and mention that `smoke-test` now checks every tool with no network access.
- **Bumping versions** (new subsection), a manual procedure:
  1. Pick a new `UBUNTU_SNAPSHOT` date and base image index digest.
  2. Re-resolve every apt pin (`apt-cache policy` after `apt-get update --snapshot <date>`) on both architectures, in both stages.
  3. Bump `KUBECTL_VERSION` and `AWS_CLI_VERSION`, and rotate `shell/linux/aws-cli.asc` if AWS changed the key.
  4. Update the tool lists in this doc and in the Dockerfile header.
  5. Bump `shell/linux/VERSION` and release as usual.

## Files to Change
- `docs/agents/tingle-linux-image.md` — toolbox groups, pinning/snapshot approach, fetch stage, `scan` step, bump procedure.

## Notes
- The user-facing docs (`docs/guides/linux.md`, `DOCKERHUB_DESCRIPTION.md`, `DOCKERHUB_SHORT_DESCRIPTION.txt`) are out of scope; they land in #236.
