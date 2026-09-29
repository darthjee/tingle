#!/usr/bin/env bash
#
# manifest.sh - Sourced helper library for tingle's MANIFEST and tingle.json.
#
# This file only defines functions: it sets no shell options (no set -e/-u)
# and runs nothing when sourced. Source it relative to the caller's location:
#   - install/installer.sh:     "$SCRIPT_DIR/manifest.sh" (its sibling)
#   - shell/update/executor.sh: "<tingle root>/install/manifest.sh"
#
# MANIFEST line format (sha256sum style), one line per shipped file:
#   <64-hex>  <path>
# i.e. the lowercase SHA-256, two spaces, then the repo-relative path. Lines
# are sorted by path with LC_ALL=C and MANIFEST does not list itself. The path
# is always the plain path (never sha256sum's "\"-prefixed escaped form).
# Consumers MUST split a line on the FIRST two spaces only: the hash is the
# text before them, the path is everything after them (further spaces
# included). Paths containing a newline are not supported.
#
# tingle.json "manifest" is either the current format
#   [{"path": "<path>", "sha256": "<64-hex>"}, ...]
# or the old path-only format written by 0.3.x and earlier
#   ["<path>", ...]
# whose entries are treated as having no hash.
#
# Dependencies: sha256sum or shasum (hashing); jq (tingle.json readers only).
# tingle_sha256 and tingle_manifest_to_json never need jq.
#
# Functions:
#
#   tingle_sha256 <file>
#     stdout: the file's 64-hex SHA-256, alone on one line.
#     status: non-zero when <file> is not a readable regular file.
#     Uses sha256sum when on PATH, else "shasum -a 256".
#
#   tingle_manifest_to_json <MANIFEST file>
#     stdout: the JSON array for tingle.json's "manifest"
#             ([{"path": ..., "sha256": ...}, ...], pretty-printed to nest
#             under "manifest": ), or [] when the file is missing or has no
#             non-blank lines. Paths are JSON-escaped (\ and ").
#     status: non-zero (message on stderr) on a malformed line: missing
#             two-space separator, hash not 64 lowercase hex, or empty path.
#
#   tingle_json_check <tingle.json>
#     stdout: nothing.
#     status: 0 when the file parses as a JSON object with "version", "repo"
#             and an array "manifest"; non-zero otherwise (E3), including
#             when jq is missing.
#
#   tingle_json_entries <tingle.json>
#     stdout: one "<hash>  <path>" line per manifest entry (MANIFEST format);
#             path-only entries print "-" as their hash.
#     status: non-zero when tingle_json_check fails.
#
#   tingle_json_tracks_hashes <tingle.json>
#     stdout: nothing.
#     status: 0 when tingle_json_check passes, the manifest has at least one
#             entry and every entry is an object with a string "sha256";
#             non-zero otherwise (path-only, mixed or []).
#

tingle_sha256() {
    local file="${1:-}" out
    if [ -z "$file" ] || [ ! -f "$file" ] || [ ! -r "$file" ]; then
        echo "tingle_sha256: cannot read file '$file'" >&2
        return 1
    fi
    if command -v sha256sum >/dev/null 2>&1; then
        out="$(sha256sum < "$file")" || return 1
    else
        out="$(shasum -a 256 < "$file")" || return 1
    fi
    printf '%s\n' "${out%% *}"
}

tingle_manifest_to_json() {
    local manifest="${1:-}" line hash path lineno=0 count=0 body=""
    if [ -z "$manifest" ] || [ ! -f "$manifest" ]; then
        printf '[]\n'
        return 0
    fi
    while IFS= read -r line || [ -n "$line" ]; do
        lineno=$((lineno + 1))
        case "$line" in
            *[![:space:]]*) ;;
            *) continue ;;
        esac
        case "$line" in
            *"  "*) ;;
            *)
                echo "tingle_manifest_to_json: $manifest:$lineno: malformed line" \
                    "(missing '<hash>  <path>' separator): $line" >&2
                return 1
                ;;
        esac
        hash="${line%%  *}"
        path="${line#*  }"
        if [ "${#hash}" -ne 64 ] || [[ "$hash" == *[!0-9a-f]* ]]; then
            echo "tingle_manifest_to_json: $manifest:$lineno: malformed line" \
                "(hash is not 64 lowercase hex): $line" >&2
            return 1
        fi
        if [ -z "$path" ]; then
            echo "tingle_manifest_to_json: $manifest:$lineno: malformed line" \
                "(empty path): $line" >&2
            return 1
        fi
        path="${path//\\/\\\\}"
        path="${path//\"/\\\"}"
        if [ "$count" -gt 0 ]; then
            body="$body,"
        fi
        body="$body"$'\n'"    {\"path\": \"$path\", \"sha256\": \"$hash\"}"
        count=$((count + 1))
    done < "$manifest"
    if [ "$count" -eq 0 ]; then
        printf '[]\n'
    else
        printf '[%s\n  ]\n' "$body"
    fi
}

tingle_json_check() {
    local file="${1:-}"
    command -v jq >/dev/null 2>&1 || return 1
    [ -n "$file" ] && [ -f "$file" ] || return 1
    jq -e '
        type == "object"
        and has("version") and has("repo") and has("manifest")
        and (.manifest | type == "array")
    ' "$file" >/dev/null 2>&1
}

tingle_json_entries() {
    local file="${1:-}"
    tingle_json_check "$file" || return 1
    jq -r '
        .manifest[]
        | if type == "string" then "-  " + .
          else ((.sha256 // "-") | tostring) + "  " + ((.path // "") | tostring)
          end
    ' "$file"
}

tingle_json_tracks_hashes() {
    local file="${1:-}"
    tingle_json_check "$file" || return 1
    jq -e '
        .manifest
        | length > 0
          and all(.[]; type == "object" and (.sha256 | type) == "string")
    ' "$file" >/dev/null 2>&1
}
