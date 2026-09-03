#!/usr/bin/env bash
#
# main.sh - Entrypoint dispatcher for the `linux` command (flow-verb protocol).
#
# Usage:
#   main.sh run <subcommand> [args...]
#
# Dependencies: executor.sh in the same directory.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
flow="$1"
shift

case "$flow" in
    run)
        exec "$SCRIPT_DIR/executor.sh" "$@"
        ;;
esac
