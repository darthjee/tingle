# Product-Owner Plan: linux shell: pass host git/ssh/kube/aws config, --isolated opt-out and banner

Main plan: [plan.md](plan.md)

## Shared contracts

Documents what `shell` produces (see [plan.md](plan.md#shared-contracts)): the host-integration table, the SSH agent rule, `--isolated`/`TINGLE_LINUX_ISOLATED`, the banner, the new 1777 directories `/home/tingle/.kube` and `/home/tingle/.config`, the extra smoke checks and `VERSION` `0.0.3`.

## Implementation Steps

### Step 1 — Update docs/agents/tingle-linux-image.md
- Image layout: `/home/tingle/.kube` and `/home/tingle/.config` are pre-created with mode 1777, and why (bind-mount parents).
- Smoke test: the foreign-uid check now also covers `$HOME/.kube` and `$HOME/.config` being writable.
- New section on `shell` host integration: the mount/env table, the SSH agent rule (Docker Desktop socket, native Linux `$SSH_AUTH_SOCK` when it's a socket, otherwise skipped), `--network host` only on native Linux Docker, the credential-helper reset, `--isolated`/`TINGLE_LINUX_ISOLATED=1` (no `docker info` call), the banner and its hardcoded tool list kept in sync with the Dockerfile, and the known limitations.
- Record the outcome of the implementation-time checks (kubectl single-file writes, ssh `host_config` ownership, Docker Desktop socket for a non-root uid) once `shell` reports them.

### Step 2 — Update docs/agents/architecture.md
Wherever `tingle linux` / `docker_run` is described, note that `shell` passes extra `docker run` args for host integration through `docker_run`'s extra-args contract, and that `sed` stays a bare `docker_run stdin`. Link to the new section in `tingle-linux-image.md`.

## Files to Change
- `docs/agents/tingle-linux-image.md` — image directories, smoke checks, host-integration section.
- `docs/agents/architecture.md` — a short note and a link.

## Notes
- Don't edit `docs/guides/`. The user guide belongs to part 4 of #231 (the `guide` agent).
