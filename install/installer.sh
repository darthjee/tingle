#!/usr/bin/env bash
#
# installer.sh - Installs an already-unpacked tingle release tree onto disk,
# either as a first install or as an in-place update of an existing one.
#
# Ships inside the release zip (alongside bin/, shell/, completions/, etc.)
# and is run from that unpacked tree (the "source"). It has two modes:
#
#   - First install (TINGLE_UPDATE_TARGET unset): normally invoked by
#     install/bootstrap.sh right after it unpacks the zip, but can also be
#     run standalone against an already-downloaded/unpacked zip.
#   - Update mode (TINGLE_UPDATE_TARGET set): normally invoked by
#     `tingle update`, which downloads and unpacks the new release and
#     hands off to the new release's installer, so the incoming code decides
#     how it is laid out on disk and the code being overwritten is never the
#     code doing the overwriting. Can also be run by hand from an unpacked
#     release.
#
# First install:
#   - Prompts for a target directory (default ~/.tingle) on /dev/tty, since
#     stdin may be occupied by a piped script. Falls back silently to the
#     default when /dev/tty is unavailable.
#   - Refuses to run if <target>/tingle.json already exists, pointing at
#     `tingle update` instead of overwriting an existing install.
#   - Copies the unpacked tree into <target> (cp -R).
#   - Writes <target>/tingle.json, embedding the release's MANIFEST.
#   - Ends with `exec "<target>/bin/tingle" install` to wire tingle into
#     ~/.bashrc.
#
# Update mode (implemented in the sibling install/update.sh). "Target" is
# the install folder, the "old manifest" is <target>/tingle.json's, the "new
# manifest" is <source>/MANIFEST. It never prompts and skips the
# "tingle.json already exists" refusal. It requires jq. Phases, in order:
#   1. Preflight (nothing changes except the lock):
#      - The target must be an existing, writable directory (named when not)
#        and must not be the source tree itself. Checked before the lock is
#        taken, so a bad target changes nothing at all.
#      - Lock: mkdir <target>/.tingle-update.lock/ (atomic) holding a "pid"
#        file with the installer's PID. A lock whose PID is running refuses
#        the run ("another update is in progress"). A lock whose process is
#        gone, or with no pid file, is stale: it is cleared (with a message)
#        and taken.
#      - The old tingle.json must parse and have "version", "repo" and
#        "manifest"; otherwise exit non-zero, nothing changed.
#      - The incoming MANIFEST must exist, be well-formed and list at least
#        one file, so a broken release tree can never prune the install.
#      - Edited-file check: every file in the old manifest is hashed. It is
#        unedited when it matches the old recorded hash OR the new
#        manifest's hash for the same path (so a re-run can finish an
#        interrupted update), or when it is missing on disk (an interrupted
#        prune). Any other mismatch aborts, listing the edited files, unless
#        TINGLE_UPDATE_FORCE=1. When the old tingle.json records no hashes
#        (the path-only format from before 0.4.0, a `version: "unknown"`
#        install from a checkout, or a hand-built install; decided by
#        format, not by version string), edits can't be
#        detected: a warning says they will be overwritten, and it goes on.
#   2. Stage: every file of the new manifest, plus MANIFEST itself, is
#      copied (permissions kept, so executables stay executable) to a temp
#      file next to its target, <dir>/.<name>.tingle-new, creating missing
#      directories. Leftovers from an earlier killed run are overwritten.
#      On any failure or signal the EXIT trap removes the staged files, the
#      directories staging created, and the lock: the install is untouched.
#   3. Swap: each staged file is renamed (mv) over its target, with INT and
#      TERM ignored for this short phase.
#   4. Prune: files in the old manifest but not in the new one are deleted,
#      then the directories they leave empty. Directories still holding
#      user-added files are kept, and files in neither manifest are never
#      touched. An empty old manifest ([]) deletes nothing and warns that
#      stale files may be left behind.
#   5. Commit: the new tingle.json is written to a temp file in the target
#      and renamed into place. Until then tingle.json still describes the
#      old version.
#   6. Wire: runs "<target>/bin/tingle install" as a child process (not
#      exec, so the traps still fire), releases the lock and prints the
#      target, the new version, and that already-open shells need a restart
#      or `source ~/.bashrc` for the new completion.
#
# Safety rules:
#   - S2: installed files are replaced by writing a temp file and renaming
#     it, never with cp in place. Bash reads a script bit by bit while it
#     runs; a rename gives the new file a new inode, so a process still
#     reading the old file (e.g. a tingle command in another terminal)
#     keeps an intact old copy.
#   - S3: in update mode the installer owns cleaning up the source tree,
#     because `tingle update` hands off with exec and keeps no trap. With
#     TINGLE_UPDATE_CLEANUP=1 the EXIT trap removes the source tree on
#     success and on failure (safe on Unix while the script runs); without
#     it (e.g. a tree the user unpacked by hand) the source is left alone.
#   - Unsafe paths: a manifest path that is absolute or has a ".." component
#     is skipped with a warning wherever it would be hashed, staged, swapped
#     or pruned, so a tampered tingle.json or MANIFEST can't touch files
#     outside the install folder.
#
# Recovery (update mode): tingle.json is written last, so wherever a run is
# cut off, re-running the update either has nothing to do or redoes it.
#   - Preflight, or stage with an error/signal: untouched; re-run from
#     scratch.
#   - Stage killed hard (kill -9, power loss): old install plus leftover
#     .tingle-new files and a stale lock; a re-run clears the lock and
#     overwrites the leftovers.
#   - Swap or prune: some or all files new, tingle.json still old, maybe a
#     stale lock; a re-run clears the lock, sees swapped files as unedited
#     (they match the incoming hash) and redoes the update, finishing the
#     prune.
#   - Commit: the rename is atomic; tingle.json is either old (as above) or
#     new (the install is fully new).
#   - Wire: fully new install; ~/.bashrc may not be rewired (re-run
#     "<target>/bin/tingle install" by hand), and a stale lock or the source
#     tree may be left behind; the next update clears the lock.
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
# Requires its siblings install/manifest.sh and install/update.sh (sourced
# helper libraries). The first-install path never calls the tingle.json
# readers, so jq stays optional there.
#
# Env vars:
#   TINGLE_REPO            - GitHub "owner/repo" recorded in tingle.json.
#                            Default: darthjee/tingle
#   TINGLE_VERSION         - Release tag recorded in tingle.json.
#                            Default: unknown
#   TINGLE_UPDATE_TARGET   - Install folder to update; setting it switches on
#                            update mode. A leading ~ is expanded and a
#                            relative path is made absolute.
#   TINGLE_UPDATE_FORCE    - "1" overwrites locally edited shipped files
#                            (update mode only).
#   TINGLE_UPDATE_CLEANUP  - "1" removes the source tree on exit (update mode
#                            only). `tingle update` sets it.
#
# Dependencies: curl, unzip, bash (required); jq (required in update mode,
# otherwise warned about), docker (warned about, not required, since it's
# needed by `tingle linux`).
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
    cat > "$tmp" <<EOF || return 1
{
  "version": "$VERSION",
  "repo": "$REPO",
  "manifest": $manifest_json
}
EOF
    mv -f "$tmp" "$target/tingle.json" || return 1
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
    update_main "$TINGLE_UPDATE_TARGET"
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
        "to already be installed there. Run 'tingle update' to update" \
        "it instead of re-running this installer." >&2
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
