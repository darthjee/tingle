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
#   docker_run <interactive: true|false> <command> [args...]
#
# Dependencies: docker.
#
set -euo pipefail

TINGLE_LINUX_IMAGE="darthjee/tingle:0.0.1"

# docker_run <interactive: true|false> <command> [args...]
docker_run() {
    local interactive="$1"
    shift

    local tty_flags=()
    if [ "$interactive" = "true" ]; then
        tty_flags=(-it)
    fi

    docker run --rm "${tty_flags[@]}" \
        --user "$(id -u):$(id -g)" \
        -v "$(pwd):$(pwd)" \
        -w "$(pwd)" \
        "$TINGLE_LINUX_IMAGE" "$@"
}
