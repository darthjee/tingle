#!/usr/bin/env bash
#
# executor.sh - Subcommand router for the `linux` command (flow verb
# protocol).
#
# Reads the subcommand name from $1 and dispatches to the matching handler
# function via a case statement. Each handler calls into docker_run (from
# docker_run.sh, sourced below) to run the real GNU/Linux tool inside the
# tingle-linux container.
#
# Usage:
#   tingle linux shell
#   tingle linux sed <sed-args...>
#
# Dependencies: docker_run.sh in the same directory; docker.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./docker_run.sh
source "$SCRIPT_DIR/docker_run.sh"

_handle_shell() {
    docker_run tty bash
}

_handle_sed() {
    docker_run stdin sed "$@"
}

subcommand="${1:-}"
[ -n "$subcommand" ] && shift

case "$subcommand" in
    shell)
        _handle_shell "$@"
        ;;
    sed)
        _handle_sed "$@"
        ;;
    *)
        echo "tingle linux: unknown subcommand '$subcommand'" >&2
        exit 1
        ;;
esac
