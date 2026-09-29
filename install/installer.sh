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
# tingle.json schema:
#   {
#     "version": "X.Y.Z",
#     "repo": "owner/repo",
#     "manifest": [
#       {"path": "bin/tingle", "sha256": "<64-hex>"}
#     ]
#   }
# "manifest" is built from the release's MANIFEST ("<64-hex>  <path>" lines)
# and is [] when there is no MANIFEST (hand-built tree) or it is empty. Paths
# are JSON-escaped (backslashes and double quotes). 0.3.x and earlier wrote a
# path-only "manifest": ["path", ...]; readers (install/manifest.sh) still
# accept it, treating those entries as having no hash.
#
# Requires its sibling install/manifest.sh (sourced helper library). The
# first-install path never calls the tingle.json readers, so jq stays
# optional here.
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

for helper in manifest.sh update.sh; do
    if [ ! -f "$SCRIPT_DIR/$helper" ]; then
        echo "installer.sh: helper library '$SCRIPT_DIR/$helper' not found;" \
            "the release tree looks incomplete" >&2
        exit 1
    fi
done
# shellcheck source=SCRIPTDIR/manifest.sh
. "$SCRIPT_DIR/manifest.sh"
# shellcheck source=SCRIPTDIR/update.sh
. "$SCRIPT_DIR/update.sh"

# normalize_target <path>
# Prints <path> with a leading ~ expanded, made absolute (a relative path is
# resolved against the current directory).
normalize_target() {
    local path="$1"
    case "$path" in
        '~') path="$HOME" ;;
        '~'/*) path="$HOME/${path#\~/}" ;;
    esac
    case "$path" in
        /*) ;;
        *) path="$(pwd)/$path" ;;
    esac
    printf '%s\n' "$path"
}

# path_is_safe <manifest path>
# Succeeds when <path> is a non-empty relative path with no ".." component,
# i.e. one that cannot point outside the install folder.
path_is_safe() {
    local path="$1"
    case "$path" in
        ''|/*) return 1 ;;
        ..|../*|*/..|*/../*) return 1 ;;
    esac
    return 0
}

# write_tingle_json <target> <manifest json>
# Writes <target>/tingle.json (VERSION, REPO and the given "manifest" array)
# to a temp file in <target>, then renames it into place.
write_tingle_json() {
    local target="$1" manifest_json="$2"
    local tmp="$target/.tingle.json.tingle-new"
    cat > "$tmp" <<EOF
{
  "version": "$VERSION",
  "repo": "$REPO",
  "manifest": $manifest_json
}
EOF
    mv -f "$tmp" "$target/tingle.json"
}

for tool in curl unzip bash; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "installer.sh: required tool '$tool' not found on PATH" >&2
        exit 1
    fi
done

if [ -n "${TINGLE_UPDATE_TARGET+set}" ]; then
    if [ -z "$TINGLE_UPDATE_TARGET" ]; then
        echo "installer.sh: TINGLE_UPDATE_TARGET is set but empty; set it to" \
            "the install folder to update" >&2
        exit 1
    fi
    if ! command -v jq >/dev/null 2>&1; then
        echo "installer.sh: update mode requires 'jq', which was not found" \
            "on PATH" >&2
        exit 1
    fi
    update_main "$(normalize_target "$TINGLE_UPDATE_TARGET")"
    exit 0
fi

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
target="$(normalize_target "${target:-$DEFAULT_TARGET}")"

if [ -f "$target/tingle.json" ]; then
    echo "installer.sh: $target/tingle.json already exists; tingle appears" \
        "to already be installed there. Use the (future) update flow" \
        "instead of re-running this installer." >&2
    exit 1
fi

if ! manifest_json="$(tingle_manifest_to_json "$SOURCE_ROOT/MANIFEST")"; then
    echo "installer.sh: $SOURCE_ROOT/MANIFEST is malformed; nothing was" \
        "installed" >&2
    exit 1
fi

mkdir -p "$target"
cp -R "$SOURCE_ROOT/." "$target/"

write_tingle_json "$target" "$manifest_json"

exec "$target/bin/tingle" install
