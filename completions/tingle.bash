#!/usr/bin/env bash
#
# tingle.bash - Bash completion hub for the `tingle` CLI.
#
# Sources the level-one (command-name) and level-two (command-argument)
# completion logic and dispatches between them based on cursor position.
#
# Usage:
#   source completions/tingle.bash
#
# This is normally installed automatically by `tingle install`, which adds
# a `source` line for this file to ~/.bashrc.
#
# Dependencies: jq (also required by bin/tingle itself).
#
TINGLE_COMPLETIONS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/bash" && pwd)"
source "$TINGLE_COMPLETIONS_DIR/tingle.sh"
source "$TINGLE_COMPLETIONS_DIR/commands.sh"

_tingle_complete() {
    if [ "$COMP_CWORD" -eq 1 ]; then
        _tingle_complete_command_names
    else
        _tingle_complete_command_args
    fi
}

complete -F _tingle_complete tingle
