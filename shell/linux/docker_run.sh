#!/usr/bin/env bash
#
# docker_run.sh - Shared container-invocation helper for `tingle linux`
# subcommands.
#
# Defines the docker_run function, a dumb wrapper around `docker run` that
# mounts the current working directory into the tingle-linux image at the
# same path and runs the given command/args inside it. It knows nothing
# about `shell`/`sed`-specific behavior — that lives in each subcommand
# handler.
#
# Usage (sourced, not executed directly):
#   source docker_run.sh
#   docker_run <mode: none|tty|stdin> <command> [args...]
#
# Modes:
#   none  - no -i, no -t (batch use)
#   tty   - -it (interactive session with a TTY, e.g. `shell`)
#   stdin - -i alone (attach stdin without allocating a TTY, e.g. `sed`)
#
# Dependencies: docker.
#
set -euo pipefail

TINGLE_LINUX_IMAGE="darthjee/tingle:0.0.1"

# docker_run <mode: none|tty|stdin> <command> [args...]
docker_run() {
    local mode="$1"
    shift

    local tty_flags=()
    case "$mode" in
        tty)
            tty_flags=(-it)
            ;;
        stdin)
            tty_flags=(-i)
            ;;
        none)
            tty_flags=()
            ;;
        *)
            echo "docker_run: unknown mode '$mode'" >&2
            return 1
            ;;
    esac

    docker run --rm "${tty_flags[@]}" \
        --user "$(id -u):$(id -g)" \
        -v "$(pwd):$(pwd)" \
        -w "$(pwd)" \
        "$TINGLE_LINUX_IMAGE" "$@"
}
