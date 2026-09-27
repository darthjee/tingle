# Shell Plan: linux shell: pass host git/ssh/kube/aws config, --isolated opt-out and banner

Main plan: [plan.md](plan.md)

## Shared contracts

This agent produces everything in [plan.md's Shared contracts](plan.md#shared-contracts): the flag and env parsing, the banner, the mounts and env forwarding, the image directories and the completion. It relies on part 2's `docker_run <mode> [docker-args...] -- <command> [args...]` (in `shell/linux/docker_run.sh`, unchanged) and on the entrypoint's `~/.ssh/host_config` wrapper.

## Steps

- [01 — Pre-create mount parents in the image and bump VERSION](shell/01-image-mount-parents.md)
- [02 — Host integration, --isolated and banner in _handle_shell](shell/02-handle-shell-host-integration.md)
- [03 — Complete --isolated after shell](shell/03-completion-isolated.md)
- [04 — Verify by hand](shell/04-verify.md)

## CI Checks
- `shell/linux/`, `scripts/release_image.sh`: run `scripts/release_image.sh build` and `scripts/release_image.sh smoke-test` locally (CI job: `build-and-publish-linux-image`). There's no shell lint or test job, so also run `shellcheck` on the touched scripts if it's available.

## Notes
- `scripts/release_image.sh` is root-level release tooling, not under `shell/`. The smoke-test change is assigned here because it's Bash and tied to the Dockerfile change. The architect reviews it.
- Keep bash 3.2 compatibility (macOS `/bin/bash`): no associative arrays, no `mapfile`, and use the `${arr[@]+"${arr[@]}"}` idiom for arrays that may be empty under `set -u`.
- Update the header comments in `executor.sh` and `completion.sh` (usage, flags, env var, dependencies: `docker info`, `uname`), as AGENTS.md requires.
