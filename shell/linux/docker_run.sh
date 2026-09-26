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
# Every container runs as the host uid:gid (the image entrypoint gives it an
# identity) and with `--security-opt no-new-privileges`.
#
# Usage (sourced, not executed directly):
#   source docker_run.sh
#   docker_run <mode: none|tty|stdin> [docker-args...] -- <command> [args...]
#
# docker-args are extra `docker run` flags (e.g. `-v src:dst`), passed after
# the built-in ones and before the image name. The `--` is required: only
# the first one is the separator, so a `--` among the command's own
# arguments (e.g. `sed -- ...`) reaches the command unchanged. Without it,
# docker_run prints an error and returns 1.
#
# Modes:
#   none  - no -i, no -t (batch use)
#   tty   - -it (interactive session with a TTY, e.g. `shell`)
#   stdin - -i alone (attach stdin without allocating a TTY, e.g. `sed`)
#
# Dependencies: docker.
#
set -euo pipefail

TINGLE_LINUX_IMAGE="darthjee/tingle:$(cat "$(dirname "${BASH_SOURCE[0]}")/VERSION")"

# docker_run <mode: none|tty|stdin> [docker-args...] -- <command> [args...]
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

    local docker_args=()
    local found_separator=false
    while [ "$#" -gt 0 ]; do
        if [ "$1" = "--" ]; then
            found_separator=true
            shift
            break
        fi
        docker_args+=("$1")
        shift
    done

    if [ "$found_separator" != true ]; then
        echo "docker_run: missing '--' before command" >&2
        return 1
    fi

    # ${arr[@]+"${arr[@]}"} keeps empty arrays safe under `set -u` on
    # bash < 4.4 (e.g. macOS's /bin/bash 3.2).
    docker run --rm ${tty_flags[@]+"${tty_flags[@]}"} \
        --user "$(id -u):$(id -g)" \
        --security-opt no-new-privileges \
        -v "$(pwd):$(pwd)" \
        -w "$(pwd)" \
        ${docker_args[@]+"${docker_args[@]}"} \
        "$TINGLE_LINUX_IMAGE" "$@"
}
