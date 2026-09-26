# Product-owner Plan: linux image: entrypoint identity via nss_wrapper and container hardening

Main plan: [plan.md](plan.md)

## Shared contracts

This agent documents the shell agent's contracts:
- entrypoint path and behavior, including the `tingle-host` identity, `HOME` and the `~/.ssh/host_config` → `~/.ssh/config` wrapper;
- the hardening (read-only `/etc/passwd`, no setuid or setgid binaries, `no-new-privileges`);
- the `docker_run <mode> [docker-args...] -- <command> [args...]` signature.

## Implementation Steps

### Step 1 — Update the tingle-linux image doc
In `docs/agents/tingle-linux-image.md`:

- **Source bullet**: replace "sets no `CMD`/`ENTRYPOINT`" with the new entrypoint and `CMD ["bash"]`, and add `libnss-wrapper` to the toolbox groups, kept in sync with the Dockerfile header.
- **New identity and hardening section**: add an entrypoint/identity and hardening section that covers:
  - why `docker_run` runs with the host uid;
  - how `nss_wrapper` gives that uid an identity without making `/etc/passwd` writable, and why making it writable was rejected (a writable passwd leads to a uid-0 entry and then root);
  - the 1777 `HOME` and `~/.ssh`;
  - the setuid/setgid strip and `no-new-privileges`;
  - the `~/.ssh/host_config` contract with #235.
- **Smoke tests**: document the new smoke checks.
- **`docker_run`**: note its new `--`-delimited signature, wherever the doc or `docs/agents/` mentions it (search with grep).

## Files to Change
- `docs/agents/tingle-linux-image.md`: entrypoint, identity, hardening and smoke-test documentation.
