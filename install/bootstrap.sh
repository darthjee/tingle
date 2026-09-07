#!/usr/bin/env bash
#
# bootstrap.sh - Web-install entry point for tingle, meant to be fetched
# fresh from `main` and piped straight into bash:
#
#   curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
#
# Downloads the pinned release zip (tingle-<tag>.zip) from GitHub Releases,
# unpacks it into a disposable work directory, and hands off to the
# installer shipped inside the zip (install/installer.sh).
#
# Kept deliberately small and boring: this is the only script ever run
# blindly via `curl | bash`, so its surface must stay easy to audit.
#
# Env vars:
#   TINGLE_REPO        - GitHub "owner/repo" to install from.
#                         Default: darthjee/tingle
#   TINGLE_VERSION      - Release tag to install (plain X.Y.Z, no "v" prefix).
#                         Default: pinned literal below.
#   TINGLE_ASSUME_YES  - When set (to any value), skips the y/N confirmation
#                         prompt. Meant as a one-off prefix, e.g.:
#                           TINGLE_ASSUME_YES=1 curl -fsSL ... | bash
#                         not something you export permanently.
#
# Dependencies: curl, unzip, bash.
#
set -euo pipefail

REPO="${TINGLE_REPO:-darthjee/tingle}"
VERSION="${TINGLE_VERSION:-0.0.1}"

for tool in curl unzip bash; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "bootstrap.sh: required tool '$tool' not found on PATH" >&2
        exit 1
    fi
done

URL="https://github.com/$REPO/releases/download/$VERSION/tingle-$VERSION.zip"
echo "This will download and install tingle from:"
echo "  $URL"

if [ -z "${TINGLE_ASSUME_YES:-}" ]; then
    if ! printf '%s' "Proceed? [y/N] " > /dev/tty 2>/dev/null; then
        echo "bootstrap.sh: no /dev/tty available to confirm; re-run with" \
            "TINGLE_ASSUME_YES=1 to skip the prompt" >&2
        exit 1
    fi

    read -r reply < /dev/tty
    case "$reply" in
        y|Y|yes|YES) ;;
        *)
            echo "Aborted."
            exit 1
            ;;
    esac
fi

WORK="$(mktemp -d)"
cleanup() {
    rm -rf "$WORK"
}
trap cleanup EXIT

curl -f -fsSL -o "$WORK/tingle.zip" "$URL"
unzip -q "$WORK/tingle.zip" -d "$WORK"

exec "$WORK/install/installer.sh"
