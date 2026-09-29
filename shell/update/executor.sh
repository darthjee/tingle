#!/usr/bin/env bash
#
# executor.sh - Updates a web install of tingle (one with tingle.json) to the
# latest stable release, or to a pinned one.
#
# This is a deliberately thin command: it resolves the target version,
# downloads and verifies the release zip into a temp dir, then hands off to
# the NEW release's install/installer.sh in update mode, which does the
# actual replacement. The code being overwritten is therefore never the code
# doing the overwriting.
#
# Usage:
#   tingle update [--check] [--force] [<version>]
#
# Inputs:
#   <version>          - Pin the target version: X.Y.Z or X.Y.Z-<suffix>, no
#                        "v" prefix. Skips the GitHub API. May be older than
#                        the installed version (downgrade) or a pre-release,
#                        but must be 0.4.0 or later.
#   TINGLE_VERSION     - Same as <version>; the argument wins when both are
#                        given.
#   --check            - Dry run: print the installed and target versions,
#                        and the locally edited shipped files when the
#                        install tracks hashes, then exit 0 without changing
#                        anything.
#   --force            - Go ahead even when shipped files were edited locally.
#                        Passed to the installer as TINGLE_UPDATE_FORCE=1.
#   TINGLE_ASSUME_YES  - When set (to any value), skip the y/N confirmation.
#
# Flow, in order (every step before the handoff that fails exits non-zero
# with nothing changed):
#   1. Detect the install: always the folder of the running bin/tingle. It
#      must be a web install (tingle.json passing tingle_json_check), and be
#      writable. A git checkout is told to use `git pull`; an unknown install
#      is refused.
#   2. Resolve the target: the pin (validated before any network call), or
#      GET <api>/releases/latest (.tag_name), the latest stable release. The
#      target must be X.Y.Z[-suffix] and 0.4.0 or later.
#   3. Up to date / --check: when the installed version equals the target,
#      print "tingle is already up to date (<version>)" and exit 0. An
#      installed version of "unknown" is always out of date. --check prints
#      "<installed> → <target>" and the edited shipped files, then exits 0.
#   4. Confirm: a y/N prompt on /dev/tty, skipped by TINGLE_ASSUME_YES.
#      Without a /dev/tty, abort with a hint to set TINGLE_ASSUME_YES.
#   5. Download and verify: fetch <base>/<version>/tingle-<version>.zip and
#      its .sha256 into a `mktemp -d` dir, check the hash, unzip, and require
#      install/installer.sh. A 404 prints
#      "release <version> not found in <repo>".
#   6. Hand off: exec <tmp>/install/installer.sh with
#      TINGLE_UPDATE_TARGET=<folder>, TINGLE_UPDATE_CLEANUP=1,
#      TINGLE_REPO=<repo from tingle.json>, TINGLE_VERSION=<target>, and
#      TINGLE_UPDATE_FORCE=1 when --force was given.
#
# Safety rule S1: this script sets NO trap (an exec drops traps anyway).
# Every failure after `mktemp -d` removes the temp dir itself before exiting,
# and the exec is the very last thing that runs. Since bin/tingle, main.sh
# and this script all exec, no process is reading a script inside the
# install folder after the handoff. TINGLE_UPDATE_CLEANUP=1 makes the
# installer remove the temp dir when it finishes or fails.
#
# Exit codes:
#   0         - Handed off successfully (the installer's own status follows),
#               already up to date, or --check.
#   non-zero  - Any refusal or failure: git checkout, unknown install,
#               corrupt tingle.json, folder not writable, invalid pin, pin
#               below 0.4.0, release not found, network failure or rate
#               limit, missing or mismatched checksum, bad zip, declined
#               confirmation, no /dev/tty without TINGLE_ASSUME_YES.
#
# Test-only hooks (NOT user-facing; do not document them elsewhere). They let
# a local folder, a file:// URL or `python3 -m http.server` stand in for
# GitHub:
#   TINGLE_RELEASE_API_URL   - Default: https://api.github.com/repos/<repo>
#   TINGLE_RELEASE_BASE_URL  - Default: https://github.com/<repo>/releases/download
#
# Dependencies: curl, unzip, jq, sha256sum or shasum; <tingle root>/install/manifest.sh.
#
set -euo pipefail

TINGLE_FOLDER="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=SCRIPTDIR/../../install/manifest.sh disable=SC1091
. "$TINGLE_FOLDER/install/manifest.sh"

usage() {
    echo "usage: tingle update [--check] [--force] [<version>]" >&2
}

CHECK=0
FORCE=0
PIN_ARG=""
HAVE_PIN_ARG=0
for arg in "$@"; do
    case "$arg" in
        --check) CHECK=1 ;;
        --force) FORCE=1 ;;
        -*)
            echo "tingle update: unknown option '$arg'" >&2
            usage
            exit 1
            ;;
        *)
            if [ "$HAVE_PIN_ARG" -eq 1 ]; then
                echo "tingle update: unexpected argument '$arg'" >&2
                usage
                exit 1
            fi
            PIN_ARG="$arg"
            HAVE_PIN_ARG=1
            ;;
    esac
done

if [ "$HAVE_PIN_ARG" -eq 1 ]; then
    PIN="$PIN_ARG"
else
    PIN="${TINGLE_VERSION:-}"
fi

# Succeeds when $1 is X.Y.Z or X.Y.Z-<suffix> (E6) and is 0.4.0 or later
# (E2); otherwise prints why on stderr and fails. Any 0.4.0-<suffix> counts
# as 0.4.0 for the floor.
validate_version() {
    local version="$1" core major minor
    if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
        echo "tingle update: invalid version '$version' (expected X.Y.Z or" \
            "X.Y.Z-<suffix>, with no 'v' prefix)" >&2
        return 1
    fi
    core="${version%%-*}"
    major="${core%%.*}"
    minor="${core#*.}"
    minor="${minor%%.*}"
    # 10# forces base 10, so a leading zero is not read as octal. The patch
    # number never matters for a X.4.0 floor.
    if [ "$((10#$major))" -eq 0 ] && [ "$((10#$minor))" -lt 4 ]; then
        echo "tingle update can only install 0.4.0 or later" >&2
        return 1
    fi
}

# --- Git checkout update path -----------------------------------------------

# Updates a git checkout of tingle. Never returns: it exits or execs.
git_update() {
    echo "tingle update: $TINGLE_FOLDER is a git checkout; update it with" \
        "'git pull' instead" >&2
    exit 1
}

# --- 1. Detect the install (E3, E14, E11) -----------------------------------

TINGLE_JSON="$TINGLE_FOLDER/tingle.json"

echo "Updating tingle in $TINGLE_FOLDER"

# tingle.json wins when both it and .git exist.
if [ ! -e "$TINGLE_JSON" ]; then
    if [ -e "$TINGLE_FOLDER/.git" ]; then
        git_update
    fi
    echo "tingle update: can't tell how tingle was installed in" \
        "$TINGLE_FOLDER (no tingle.json and not a git checkout); nothing" \
        "was changed" >&2
    exit 1
fi

# --- Web install path -------------------------------------------------------

for tool in curl unzip jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "tingle update: required tool '$tool' not found on PATH" >&2
        exit 1
    fi
done

# A pin is validated before any network call (E6, E2).
if [ -n "$PIN" ]; then
    validate_version "$PIN" || exit 1
fi

if ! tingle_json_check "$TINGLE_JSON"; then
    echo "tingle update: $TINGLE_JSON is corrupt (it can't be parsed, or" \
        "'version', 'repo' or 'manifest' is missing); nothing was changed" >&2
    exit 1
fi
INSTALLED="$(jq -r '.version | tostring' "$TINGLE_JSON")"
REPO="$(jq -r '.repo | tostring' "$TINGLE_JSON")"

if [ ! -w "$TINGLE_FOLDER" ]; then
    echo "tingle update: the install folder $TINGLE_FOLDER is not writable" >&2
    exit 1
fi

# --- 2. Resolve the target (E2, E6, E8, E10) --------------------------------

API_URL="${TINGLE_RELEASE_API_URL:-https://api.github.com/repos/$REPO}"
BASE_URL="${TINGLE_RELEASE_BASE_URL:-https://github.com/$REPO/releases/download}"

PIN_HINT="pin a version to skip the lookup, e.g. 'tingle update X.Y.Z'"

if [ -n "$PIN" ]; then
    TARGET="$PIN"
else
    # No auth header: tingle never handles a GitHub token. The body and the
    # HTTP status are captured together (status on the last line) so that no
    # temp file is needed here.
    if ! response="$(curl -sS -w '\n%{http_code}' "$API_URL/releases/latest")"; then
        echo "tingle update: could not reach $API_URL to find the latest" \
            "release (network failure); $PIN_HINT" >&2
        exit 1
    fi
    status="${response##*$'\n'}"
    body="${response%$'\n'*}"
    # file:// (test hooks) reports no HTTP status: a successful curl is a 200.
    if [ "$status" = "000" ]; then
        status=200
    fi
    case "$status" in
        200) ;;
        403|429)
            echo "tingle update: the GitHub API rate limit was hit (HTTP" \
                "$status) while looking up the latest release; $PIN_HINT" >&2
            exit 1
            ;;
        *)
            echo "tingle update: unexpected response (HTTP $status) from" \
                "$API_URL/releases/latest; $PIN_HINT" >&2
            exit 1
            ;;
    esac
    TARGET="$(printf '%s\n' "$body" | jq -r '.tag_name // empty' 2>/dev/null)" || TARGET=""
    if [ -z "$TARGET" ] || [ "$TARGET" = "null" ]; then
        echo "tingle update: could not read the latest release's tag_name" \
            "from $API_URL/releases/latest; $PIN_HINT" >&2
        exit 1
    fi
    validate_version "$TARGET" || exit 1
fi

# --- 3. Up to date and --check (E4) -----------------------------------------

# "unknown" (a standalone install) is always out of date.
if [ "$INSTALLED" != "unknown" ] && [ "$INSTALLED" = "$TARGET" ]; then
    echo "tingle is already up to date ($TARGET)"
    exit 0
fi

echo "$INSTALLED → $TARGET"

if [ "$CHECK" -eq 1 ]; then
    if tingle_json_tracks_hashes "$TINGLE_JSON"; then
        edited=""
        while IFS= read -r entry; do
            hash="${entry%%  *}"
            path="${entry#*  }"
            case "$path" in
                ""|/*|..|../*|*/..|*/../*) continue ;;
            esac
            file="$TINGLE_FOLDER/$path"
            if [ ! -f "$file" ] || [ -L "$file" ]; then
                continue
            fi
            current="$(tingle_sha256 "$file")" || continue
            if [ "$current" != "$hash" ]; then
                edited="$edited  $path"$'\n'
            fi
        done < <(tingle_json_entries "$TINGLE_JSON")
        if [ -n "$edited" ]; then
            echo "Locally edited shipped files (use --force to overwrite them):"
            printf '%s' "$edited"
        fi
    fi
    exit 0
fi

# --- 4. Confirmation --------------------------------------------------------

if [ -z "${TINGLE_ASSUME_YES:-}" ]; then
    # The group makes 2>/dev/null also hide the error from opening /dev/tty.
    if ! { printf '%s' "Proceed? [y/N] " > /dev/tty; } 2>/dev/null; then
        echo "tingle update: no /dev/tty available to confirm; re-run with" \
            "TINGLE_ASSUME_YES=1 to skip the prompt" >&2
        exit 1
    fi

    reply=""
    read -r reply < /dev/tty || true
    case "$reply" in
        y|Y|yes|YES) ;;
        *)
            echo "Aborted."
            exit 1
            ;;
    esac
fi

# --- 5. Download and verify (E7, E8, E9, E9b) -------------------------------

# S1: no trap here. Every failure from now on goes through fail, which
# removes the temp dir itself before exiting.
WORK="$(mktemp -d)"

fail() {
    rm -rf "$WORK"
    echo "tingle update: $*" >&2
    exit 1
}

# fetch <url> <dest>: downloads <url> into <dest> and prints the HTTP status
# ("200" on success). A curl failure prints "000", or "404" for a file:// URL
# (a missing local file); file:// reports no status, so success is a 200.
fetch() {
    local url="$1" dest="$2" code
    if code="$(curl -L -sS -o "$dest" -w '%{http_code}' "$url")"; then
        if [ "$code" = "000" ]; then
            code=200
        fi
    else
        case "$url" in
            file://*) code=404 ;;
            *) code=000 ;;
        esac
    fi
    printf '%s\n' "$code"
}

ZIP_NAME="tingle-$TARGET.zip"
ZIP_URL="$BASE_URL/$TARGET/$ZIP_NAME"
ZIP="$WORK/$ZIP_NAME"

status="$(fetch "$ZIP_URL" "$ZIP")"
case "$status" in
    200) ;;
    404)
        rm -rf "$WORK"
        echo "release $TARGET not found in $REPO" >&2
        exit 1
        ;;
    403|429)
        fail "the GitHub rate limit was hit (HTTP $status) while downloading" \
            "$ZIP_URL; try again later"
        ;;
    000)
        fail "could not download $ZIP_URL (network failure); nothing was changed"
        ;;
    *)
        fail "unexpected response (HTTP $status) while downloading $ZIP_URL;" \
            "nothing was changed"
        ;;
esac

status="$(fetch "$ZIP_URL.sha256" "$ZIP.sha256")"
if [ "$status" != "200" ]; then
    fail "could not download the checksum $ZIP_URL.sha256 (HTTP $status);" \
        "nothing was changed"
fi

expected="$(awk 'NR == 1 { print $1; exit }' "$ZIP.sha256")"
actual="$(tingle_sha256 "$ZIP")" || actual=""
if [ -z "$expected" ] || [ "$expected" != "$actual" ]; then
    fail "checksum mismatch for $ZIP_NAME (expected '$expected', got" \
        "'$actual'); the download was deleted and nothing was changed"
fi

if ! unzip -q "$ZIP" -d "$WORK"; then
    fail "$ZIP_NAME could not be unzipped; nothing was changed"
fi

if [ ! -f "$WORK/install/installer.sh" ] || [ ! -x "$WORK/install/installer.sh" ]; then
    fail "$ZIP_NAME has no executable install/installer.sh; nothing was changed"
fi

# --- 6. Hand off (S1) -------------------------------------------------------

# The installer's EXIT trap removes $WORK (TINGLE_UPDATE_CLEANUP=1). Nothing
# may run after this exec.
# Only --force may reach the installer as TINGLE_UPDATE_FORCE=1.
if [ "$FORCE" -eq 1 ]; then
    export TINGLE_UPDATE_FORCE=1
else
    unset TINGLE_UPDATE_FORCE
fi
TINGLE_UPDATE_TARGET="$TINGLE_FOLDER" TINGLE_UPDATE_CLEANUP=1 \
TINGLE_REPO="$REPO" TINGLE_VERSION="$TARGET" \
exec "$WORK/install/installer.sh"
