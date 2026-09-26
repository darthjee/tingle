# Shell Plan: linux image: entrypoint identity via nss_wrapper and container hardening

Main plan: [plan.md](plan.md)

## Shared contracts

This agent produces every contract in [plan.md](plan.md#shared-contracts):
- the entrypoint path and behavior;
- the image `ENTRYPOINT` and `CMD`;
- the 1777 permissions and the setuid/setgid strip;
- the `~/.ssh/config` wrapper;
- the `docker_run <mode> [docker-args...] -- <command> [args...]` signature with `no-new-privileges`.

## Steps

- [01 — Add the entrypoint script](shell/01-add-entrypoint-script.md)
- [02 — Wire the entrypoint and hardening into the Dockerfile](shell/02-dockerfile-entrypoint-and-hardening.md)
- [03 — Extend docker_run and update its callers](shell/03-docker-run-extra-args-and-no-new-privileges.md)

## Notes
- Don't bump `shell/linux/VERSION` here. The next release (0.1.0) happens in #236.
- Resolve the `libnss-wrapper` version against `UBUNTU_SNAPSHOT=20260920T000000Z`, the same way the other pins were resolved. For example, run `apt-cache policy libnss-wrapper` inside a container that has the snapshot sources set up.
- `tingle linux sed`'s output, stdin handling and exit codes must not change, and the entrypoint must never print anything.
