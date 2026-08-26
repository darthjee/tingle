#!/usr/bin/env bash
#
# install.sh - Installs tingle onto PATH and enables its bash completion.
#
# Appends a marker block to ~/.bashrc that:
#   - Adds the repo's bin/ folder to PATH.
#   - Sources the repo's completions/tingle.bash script.
#
# The operation is idempotent: running it more than once will not duplicate
# the block, and it never overwrites or rewrites any other content already
# present in ~/.bashrc.
#
# Usage:
#   tingle install
#
# Dependencies: none beyond a standard POSIX/bash environment.
#
set -euo pipefail

TINGLE_FOLDER="$(cd "$(dirname "$0")/.." && pwd)"
BASHRC="$HOME/.bashrc"

MARKER_START="# >>> tingle >>>"
MARKER_END="# <<< tingle <<<"

[ -f "$BASHRC" ] || touch "$BASHRC"

if grep -qF "$MARKER_START" "$BASHRC"; then
    echo "tingle is already installed in $BASHRC"
    exit 0
fi

{
    echo ""
    echo "$MARKER_START"
    echo "export PATH=\"$TINGLE_FOLDER/bin:\$PATH\""
    echo "source \"$TINGLE_FOLDER/completions/tingle.bash\""
    echo "$MARKER_END"
} >> "$BASHRC"

echo "tingle installed. Run 'source $BASHRC' or restart your shell to start using it."
