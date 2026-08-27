# Split completions/tingle.bash and add level-two delegation

`completions/tingle.bash` currently holds both the shell registration
(`complete -F ... tingle`) and the level-one (command-name) completion logic
in a single `_tingle_complete` function. Split it into a central hub plus
two dedicated files, and add level-two (command-argument) delegation using
the `tingle resolve <cmd>` helper from
[01-bin-tingle-flow-verb-and-resolve.md](01-bin-tingle-flow-verb-and-resolve.md)
(shared contract 5) and the file-presence feature detection + generic
fallback (shared contract 3).

## `completions/tingle.bash` (central hub)

Sources the two files below and registers a single dispatcher that routes
by `COMP_CWORD`:

```bash
#!/usr/bin/env bash
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
```

## `completions/bash/tingle.sh` (level one — command names)

Move today's `_tingle_complete` body here, renamed to
`_tingle_complete_command_names`, dropping the `COMP_CWORD -ne 1` guard (now
handled by the hub's dispatcher above) and the trailing `complete -F ...`
registration line (also moved to the hub). Logic (command discovery from
`commands/*.json`, dedup, load order) is otherwise unchanged from the
current `completions/tingle.bash`.

## `completions/bash/commands.sh` (level two — delegate to commands)

New file implementing the delegate-or-fallback behavior:

```bash
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
```

`tingle resolve <cmd>` fails (non-zero exit, empty output) for an unknown
command — `_tingle_complete_command_args` returns with no suggestions in
that case rather than erroring.

## Files to Change

- `completions/tingle.bash` — reduced to the central hub (sourcing + dispatcher + `complete -F` registration).
- `completions/bash/tingle.sh` — new, level-one command-name completion (moved from the current `completions/tingle.bash`).
- `completions/bash/commands.sh` — new, level-two delegation + generic file/folder fallback.
