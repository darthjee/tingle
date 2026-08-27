#!/usr/bin/env bash
#
# commands.sh - Level-two bash completion for the `tingle` CLI hub.
#
# Completes `tingle <cmd> <TAB>` by delegating to the resolved command's own
# completion handler (completion.<ext> next to its main.<ext>, invoked with a
# `complete` flow verb), falling back to generic file/folder completion when
# the command has no dedicated completion handler.
#

_tingle_complete_command_args() {
    local tingle_folder cmd main_path cmd_dir ext completion_file cur

    tingle_folder="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    cmd="${COMP_WORDS[1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"

    main_path="$("$tingle_folder/bin/tingle" resolve "$cmd" 2>/dev/null)" || return 0
    [ -n "$main_path" ] || return 0

    cmd_dir="$(dirname "$main_path")"
    ext="${main_path##*.}"
    completion_file="$cmd_dir/completion.$ext"

    if [ -f "$completion_file" ]; then
        # Raw argv, including the trailing (possibly empty) current word —
        # see shared contract 4. The completion handler must not use a
        # strict parser (e.g. argparse) on this.
        COMPREPLY=($(compgen -W "$("$main_path" complete "${COMP_WORDS[@]:2}")" -- "$cur"))
    else
        # Generic fallback: native file/folder completion (shared contract 3).
        COMPREPLY=($(compgen -f -- "$cur"))
        compopt -o filenames 2>/dev/null || true
    fi
}
