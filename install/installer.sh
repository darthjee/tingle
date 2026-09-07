#!/usr/bin/env bash
#
# installer.sh - Installs an already-unpacked tingle release tree onto disk.
#
# Ships inside the release zip (alongside bin/, shell/, completions/, etc.)
# and is normally invoked by install/bootstrap.sh right after it unpacks the
# zip, but can also be run standalone against an already-downloaded/unpacked
# zip.
#
# Behavior:
#   - Prompts for a target directory (default ~/.tingle) on /dev/tty, since
#     stdin may be occupied by a piped script. Falls back silently to the
#     default when /dev/tty is unavailable.
#   - Refuses to run if <target>/tingle.json already exists (points at a
#     future `update` flow instead of overwriting an existing install).
#   - Copies the unpacked tree into <target>.
#   - Writes <target>/tingle.json, embedding the release's MANIFEST.
#   - Runs "<target>/bin/tingle install" to wire tingle into ~/.bashrc.
#
# Env vars (inherited from bootstrap.sh, or defaulted when run standalone):
#   TINGLE_REPO     - GitHub "owner/repo" recorded in tingle.json.
#                     Default: darthjee/tingle
#   TINGLE_VERSION  - Release tag recorded in tingle.json.
#                     Default: unknown
#
# Dependencies: curl, unzip, bash (required); jq, docker (warned about, not
# required, since they're needed by bin/tingle and `tingle linux`
# respectively).
#
set -euo pipefail

REPO="${TINGLE_REPO:-darthjee/tingle}"
VERSION="${TINGLE_VERSION:-unknown}"
DEFAULT_TARGET="$HOME/.tingle"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

for tool in curl unzip bash; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "installer.sh: required tool '$tool' not found on PATH" >&2
        exit 1
    fi
done

for tool in jq docker; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "installer.sh: warning: '$tool' not found on PATH; some tingle" \
            "commands may not work until it is installed" >&2
    fi
done

target=""
if printf '%s' "Install tingle to [$DEFAULT_TARGET]: " > /dev/tty 2>/dev/null; then
    read -r target < /dev/tty || target=""
fi
target="${target:-$DEFAULT_TARGET}"

# Expand a leading ~ and normalize relative paths.
case "$target" in
    '~') target="$HOME" ;;
    '~'/*) target="$HOME/${target#\~/}" ;;
esac
case "$target" in
    /*) ;;
    *) target="$(pwd)/$target" ;;
esac

if [ -f "$target/tingle.json" ]; then
    echo "installer.sh: $target/tingle.json already exists; tingle appears" \
        "to already be installed there. Use the (future) update flow" \
        "instead of re-running this installer." >&2
    exit 1
fi

mkdir -p "$target"
cp -R "$SOURCE_ROOT/." "$target/"

manifest_json="[]"
if [ -f "$SOURCE_ROOT/MANIFEST" ]; then
    manifest_json="$(
        awk 'NF { gsub(/\\/, "\\\\", $0); gsub(/"/, "\\\"", $0); printf "%s\"%s\"", (NR>1 ? ",\n    " : "\n    "), $0 } END { print "\n  " }' \
            "$SOURCE_ROOT/MANIFEST"
    )"
    manifest_json="[$manifest_json]"
fi

cat > "$target/tingle.json" <<EOF
{
  "version": "$VERSION",
  "repo": "$REPO",
  "manifest": $manifest_json
}
EOF

exec "$target/bin/tingle" install
