#!/usr/bin/env bash
#
# executor.sh - Installs tingle onto PATH and enables its bash completion.
#
# Appends a marker block to ~/.bashrc that:
#   - Adds the repo's bin/ folder to PATH.
#   - Sources the repo's completions/tingle.bash script.
#
# The block is delimited by the lines "# >>> tingle >>>" and
# "# <<< tingle <<<". Behavior when run:
#   - No block yet: the block is appended (preceded by a blank line).
#   - Block present and pointing to this tingle folder: nothing changes.
#   - Block present but pointing to another folder (the repo was moved or
#     re-cloned elsewhere): the block is rewritten in place to point to this
#     folder. Everything outside the markers is left untouched.
#   - Start marker without a matching end marker: nothing is changed and the
#     script exits non-zero, asking you to fix ~/.bashrc by hand.
#
# ~/.bashrc is written back through the existing file (not replaced), so a
# symlinked ~/.bashrc and its permissions are preserved.
#
# Only bash (~/.bashrc) is supported; zsh, fish and other shells are not.
# On macOS, bash login shells read ~/.bash_profile, which must source
# ~/.bashrc for this to take effect.
#
# Usage:
#   tingle install
#
# Dependencies: none beyond a standard POSIX/bash environment (awk, grep,
# mktemp).
#
set -euo pipefail

TINGLE_FOLDER="$(cd "$(dirname "$0")/../.." && pwd)"
BASHRC="$HOME/.bashrc"

MARKER_START="# >>> tingle >>>"
MARKER_END="# <<< tingle <<<"

# Prints the marker block pointing to $TINGLE_FOLDER.
generate_block() {
    echo "$MARKER_START"
    echo "export PATH=\"$TINGLE_FOLDER/bin:\$PATH\""
    echo "source \"$TINGLE_FOLDER/completions/tingle.bash\""
    echo "$MARKER_END"
}

# Succeeds if the first start marker in $BASHRC has a matching end marker.
block_is_closed() {
    awk -v s="$MARKER_START" -v e="$MARKER_END" '
        !started && $0 == s { started = 1; next }
        started && $0 == e  { closed = 1; exit }
        END { exit(closed ? 0 : 1) }
    ' "$BASHRC"
}

# Prints the tingle folder recorded in the block's `export PATH=` line, or
# nothing if it cannot be parsed.
installed_folder() {
    awk -v s="$MARKER_START" -v e="$MARKER_END" '
        BEGIN { prefix = "export PATH=\""; suffix = "/bin:$PATH\"" }
        !started && $0 == s { started = 1; next }
        started && $0 == e  { exit }
        started && index($0, prefix) == 1 {
            rest = substr($0, length(prefix) + 1)
            n = length(rest) - length(suffix)
            if (n > 0 && substr(rest, n + 1) == suffix) {
                print substr(rest, 1, n)
            }
            exit
        }
    ' "$BASHRC"
}

# Replaces the first marker block (markers included) with a fresh one.
rewrite_block() {
    local tmp
    tmp="$(mktemp)"
    trap 'rm -f "$tmp"' EXIT

    {
        awk -v s="$MARKER_START" '$0 == s { exit } { print }' "$BASHRC"
        generate_block
        awk -v s="$MARKER_START" -v e="$MARKER_END" '
            done                   { print; next }
            !started && $0 == s    { started = 1; next }
            started && $0 == e     { done = 1 }
        ' "$BASHRC"
    } > "$tmp"

    cat "$tmp" > "$BASHRC"
    rm -f "$tmp"
    trap - EXIT
}

[ -f "$BASHRC" ] || touch "$BASHRC"

if grep -qxF "$MARKER_START" "$BASHRC"; then
    if ! block_is_closed; then
        echo "Error: $BASHRC has a '$MARKER_START' line without a matching '$MARKER_END' line. Fix $BASHRC by hand and run 'tingle install' again." >&2
        exit 1
    fi

    if [ "$(installed_folder)" = "$TINGLE_FOLDER" ]; then
        echo "tingle is already installed in $BASHRC"
        exit 0
    fi

    rewrite_block
    echo "tingle install updated in $BASHRC (now pointing to $TINGLE_FOLDER). Run 'source $BASHRC' or restart your shell to pick it up."
    exit 0
fi

{
    echo ""
    generate_block
} >> "$BASHRC"

echo "tingle installed. Run 'source $BASHRC' or restart your shell to start using it."
