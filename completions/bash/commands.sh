#!/usr/bin/env bash
#
# commands.sh - Level-two bash completion for the `tingle` CLI hub.
#
# Completes `tingle <cmd> <TAB>` by delegating to the resolved command's own
# completion handler (completion.<ext> next to its main.<ext>, invoked with a
# `complete` flow verb), falling back to generic file/folder completion when
# the command has no dedicated completion handler.
#
# A completion handler may also ask for that same file/folder fallback by
# printing only the sentinel word `__tingle_files__` (surrounding whitespace
# is ignored). Any other output, including empty output, is used as the list
# of candidate words.
#

# Reserved word a completion handler prints to request file/folder completion.
_TINGLE_FILES_SENTINEL="__tingle_files__"

# Native file/folder completion for the current word.
_tingle_complete_files() {
    COMPREPLY=($(compgen -f -- "$1"))
    compopt -o filenames 2>/dev/null || true
}

_tingle_complete_command_args() {
    local tingle_folder cmd main_path cmd_dir ext completion_file cur out trimmed

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
        out="$("$main_path" complete "${COMP_WORDS[@]:2}")"
        trimmed="${out#"${out%%[![:space:]]*}"}"
        trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
        if [ "$trimmed" = "$_TINGLE_FILES_SENTINEL" ]; then
            _tingle_complete_files "$cur"
        else
            COMPREPLY=($(compgen -W "$out" -- "$cur"))
        fi
    else
        # Generic fallback: native file/folder completion (shared contract 3).
        _tingle_complete_files "$cur"
    fi
}
