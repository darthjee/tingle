#!/usr/bin/env bash
#
# completion.sh - Bash completion handler for the `linux` command (flow verb
# protocol).
#
# Receives the raw argv from the subcommand onward, with the word currently
# being typed last (possibly empty). Only the committed words (all but the
# last) are inspected, and no strict parsing is applied. Prints:
#   - the subcommand list, when no word has been committed yet;
#   - the `__tingle_files__` sentinel after `sed`, so the completion hub
#     falls back to native file/folder completion;
#   - nothing otherwise (e.g. after `shell`).
# Always exits 0 and never starts Docker.
#
# Usage:
#   main.sh complete [<words...>] <current-word>
#
# Dependencies: none.
#
set -euo pipefail

# Must match the subcommands handled by the case statement in executor.sh.
SUBCOMMANDS="shell sed"
FILES_SENTINEL="__tingle_files__"

committed=()
if [ "$#" -gt 1 ]; then
    committed=("${@:1:$(($# - 1))}")
fi

if [ "${#committed[@]}" -eq 0 ]; then
    echo "$SUBCOMMANDS"
    exit 0
fi

case "${committed[0]}" in
    sed)
        echo "$FILES_SENTINEL"
        ;;
    *)
        ;;
esac

exit 0
