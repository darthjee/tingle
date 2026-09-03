# Issue: Execution: shell subcommand (the anchor command)

## Description
Wire the `shell` subcommand of `tingle linux` (stubbed out in #36) through the existing `docker_run` helper to run an interactive `/bin/bash` shell inside the `tingle-linux` container (built in #35), with the current working directory mounted at the same path.

## Problem
`_handle_shell` in `shell/linux/executor.sh` is currently a stub that prints "not implemented yet" and exits 1 — there is no way yet to get an interactive Linux shell via `tingle linux shell`.

## Expected Behavior
Running `tingle linux shell` from any directory:
- Starts an interactive `bash` session inside the `tingle-linux` container.
- Mounts the current working directory into the container at the same path and sets it as the container's working directory.
- Runs as the host user's uid:gid (already handled by `docker_run`), so files created/edited from the shell are owned by the host user on exit.
- Removes the container automatically on exit (`docker run --rm`), leaving nothing behind (`docker ps -a` shows nothing lingering).

## Solution
- Replace the `_handle_shell` stub in `shell/linux/executor.sh` with a call to the existing `docker_run` helper: `docker_run true bash` (interactive=true, command=bash).
- Add a concrete usage example for `tingle linux shell` to `commands/shell.json`'s `long_help` for `linux`.
- Manual verification: run `tingle linux shell` from a repo directory; confirm the cwd is mounted and browsable; confirm files created inside the shell are host-owned on exit; confirm the container is gone after exiting (`docker ps -a` shows nothing lingering).

## Benefits
Delivers the first real, usable subcommand of `tingle linux` — an interactive Linux shell — validating the `docker_run` container-invocation model end-to-end before the `sed` subcommand builds on the same foundation.
