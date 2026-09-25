#!/usr/bin/env bash
#
# main.sh - Entrypoint dispatcher for the `linux` command (flow-verb protocol).
#
# Usage:
#   main.sh run <subcommand> [args...]
#   main.sh complete [args...]
#
# Dependencies: executor.sh and completion.sh in the same directory.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
flow="$1"
shift

case "$flow" in
    run)
        exec "$SCRIPT_DIR/executor.sh" "$@"
        ;;
    complete)
        exec "$SCRIPT_DIR/completion.sh" "$@"
        ;;
esac
