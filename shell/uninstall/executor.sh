#!/usr/bin/env bash
#
# executor.sh - Removes the tingle wiring added by `tingle install`.
#
# Deletes the marker block (the lines "# >>> tingle >>>" through
# "# <<< tingle <<<", markers included) from ~/.bashrc, along with the single
# blank line right before it that `tingle install` added. All other content in
# ~/.bashrc is left untouched, and the file is written back through the
# existing file, so a symlinked ~/.bashrc and its permissions are preserved.
#
# The tingle folder itself is never deleted; remove it by hand if you no
# longer need it.
#
# Behavior when run:
#   - No ~/.bashrc, or no marker block: reports that tingle is not installed
#     and exits 0 (the file is not created).
#   - Start marker without a matching end marker: nothing is changed and the
#     script exits non-zero, asking you to fix ~/.bashrc by hand.
#
# Only bash (~/.bashrc) is supported.
#
# Usage:
#   tingle uninstall
#
# Dependencies: none beyond a standard POSIX/bash environment (awk, grep,
# mktemp).
#
set -euo pipefail

TINGLE_FOLDER="$(cd "$(dirname "$0")/../.." && pwd)"
BASHRC="$HOME/.bashrc"

MARKER_START="# >>> tingle >>>"
MARKER_END="# <<< tingle <<<"

# Succeeds if the first start marker in $BASHRC has a matching end marker.
block_is_closed() {
    awk -v s="$MARKER_START" -v e="$MARKER_END" '
        !started && $0 == s { started = 1; next }
        started && $0 == e  { closed = 1; exit }
        END { exit(closed ? 0 : 1) }
    ' "$BASHRC"
}

# Prints $BASHRC without the first marker block and the blank line directly
# before it.
strip_block() {
    awk -v s="$MARKER_START" -v e="$MARKER_END" '
        inblock { if ($0 == e) inblock = 0; next }
        !done && $0 == s { inblock = 1; done = 1; pending = 0; next }
        {
            if (pending) { print ""; pending = 0 }
            if ($0 == "") { pending = 1; next }
            print
        }
        END { if (pending) print "" }
    ' "$BASHRC"
}

if [ ! -f "$BASHRC" ] || ! grep -qxF "$MARKER_START" "$BASHRC"; then
    echo "tingle is not installed in $BASHRC"
    exit 0
fi

if ! block_is_closed; then
    echo "Error: $BASHRC has a '$MARKER_START' line without a matching '$MARKER_END' line. Fix $BASHRC by hand and run 'tingle uninstall' again." >&2
    exit 1
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

strip_block > "$tmp"
cat "$tmp" > "$BASHRC"

echo "tingle uninstalled from $BASHRC. Restart your shell to drop it from PATH. The tingle folder ($TINGLE_FOLDER) was left in place; delete it manually if you no longer need it."
