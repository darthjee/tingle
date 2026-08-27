#!/usr/bin/env bash
#
# tingle.sh - Level-one bash completion for the `tingle` CLI hub.
#
# Completes `tingle <TAB>` with the command names registered in
# commands/*.json, following the exact same load order and first-file-wins
# dedup rule as bin/tingle. Only top-level command names are completed here;
# argument/flag completion is delegated to completions/bash/commands.sh.
#
# Dependencies: jq (also required by bin/tingle itself).
#

_tingle_complete_command_names() {
    local tingle_folder commands_dir cmd_file cmd_files names cur

    tingle_folder="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    commands_dir="$tingle_folder/commands"

    cur="${COMP_WORDS[COMP_CWORD]}"

    if ! command -v jq >/dev/null 2>&1; then
        return 0
    fi

    shopt -s nullglob
    cmd_files=("$commands_dir"/*.json)
    shopt -u nullglob

    # Deterministic, alphabetical load order (matches bin/tingle).
    IFS=$'\n' cmd_files=($(printf '%s\n' "${cmd_files[@]}" | sort)); unset IFS

    local -a command_names=()

    for cmd_file in "${cmd_files[@]}"; do
        jq empty "$cmd_file" >/dev/null 2>&1 || continue

        while IFS= read -r name; do
            [ -z "$name" ] && continue

            local existing
            for existing in "${command_names[@]}"; do
                if [ "$existing" = "$name" ]; then
                    continue 2
                fi
            done

            command_names+=("$name")
        done < <(jq -r 'keys_unsorted[]' "$cmd_file" 2>/dev/null)
    done

    COMPREPLY=($(compgen -W "${command_names[*]}" -- "$cur"))
}
