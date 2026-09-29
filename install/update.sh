#!/usr/bin/env bash
#
# update.sh - Sourced helper library holding install/installer.sh's update
# mode. The behaviour (trigger, env vars, lock, phases, safety rules and
# recovery) is documented in the header of install/installer.sh.
#
# This file only defines functions and a few empty globals: it sets no shell
# options and runs nothing when sourced. It relies on the globals and helpers
# installer.sh defines before calling update_main (REPO, VERSION,
# SOURCE_ROOT, normalize_target, path_is_safe, write_tingle_json) and on
# install/manifest.sh. Bash 3.2 compatible: no associative arrays, no
# mapfile; "is this path listed" lookups use temp files and grep -F -x.
#
# Functions:
#
#   update_main <raw target>
#     Normalizes <raw target> (TINGLE_UPDATE_TARGET) and runs every update
#     phase against it. Exits non-zero on any refusal or failure; the EXIT
#     trap (update_on_exit) always releases the lock, removes staged files
#     when interrupted while staging, and removes the source tree when
#     TINGLE_UPDATE_CLEANUP=1.
#

UPDATE_TARGET=""
UPDATE_LOCK=""
UPDATE_WORK=""
UPDATE_PHASE=""

update_die() {
    echo "installer.sh: $*" >&2
    exit 1
}

update_warn() {
    echo "installer.sh: warning: $*" >&2
}

# update_on_exit
# EXIT trap: releases the lock, drops the scratch dir and, when
# TINGLE_UPDATE_CLEANUP=1, removes the source tree. Keeps the exit status.
update_on_exit() {
    local status=$?
    trap '' INT TERM
    if [ "$UPDATE_PHASE" = "stage" ]; then
        update_unstage
    fi
    if [ -n "$UPDATE_LOCK" ]; then
        rm -rf "$UPDATE_LOCK"
    fi
    if [ -n "$UPDATE_WORK" ]; then
        rm -rf "$UPDATE_WORK"
    fi
    if [ "${TINGLE_UPDATE_CLEANUP:-}" = "1" ]; then
        case "$SOURCE_ROOT" in
            ''|/|"$HOME"|"$UPDATE_TARGET")
                update_warn "not removing the source tree '$SOURCE_ROOT'" ;;
            *) rm -rf "$SOURCE_ROOT" ;;
        esac
    fi
    exit "$status"
}

# update_staged_name <path>
# Prints the staged temp file for manifest <path>: <dir>/.<name>.tingle-new
# in the target, next to the file it will replace.
update_staged_name() {
    local path="$1"
    case "$path" in
        */*) printf '%s\n' "$UPDATE_TARGET/${path%/*}/.${path##*/}.tingle-new" ;;
        *) printf '%s\n' "$UPDATE_TARGET/.$path.tingle-new" ;;
    esac
}

# update_unstage
# Removes every staged file, then the directories staging created (deepest
# first, only while empty), leaving the install as it was.
update_unstage() {
    local staged
    if [ -f "$UPDATE_WORK/staged" ]; then
        while IFS= read -r staged; do
            rm -f -- "$staged"
        done < "$UPDATE_WORK/staged"
    fi
    if [ -f "$UPDATE_WORK/created_dirs" ]; then
        awk '{ line[NR] = $0 } END { for (i = NR; i > 0; i--) print line[i] }' \
            "$UPDATE_WORK/created_dirs" \
            | while IFS= read -r staged; do
                rmdir -- "$staged" 2>/dev/null || true
            done
    fi
}

# update_check_target
# Fails early, naming the folder, unless the target is an existing writable
# directory distinct from the source tree.
update_check_target() {
    if [ ! -d "$UPDATE_TARGET" ]; then
        update_die "install folder '$UPDATE_TARGET' does not exist or is not" \
            "a directory"
    fi
    if [ ! -w "$UPDATE_TARGET" ]; then
        update_die "install folder '$UPDATE_TARGET' is not writable; nothing" \
            "was changed"
    fi
    if [ "$(cd "$UPDATE_TARGET" && pwd -P)" = "$(cd "$SOURCE_ROOT" && pwd -P)" ]; then
        update_die "the release tree '$SOURCE_ROOT' is the install folder" \
            "itself; run the installer from an unpacked release instead"
    fi
}

# update_take_lock
# Takes <target>/.tingle-update.lock/ (mkdir is atomic) and records $$ in its
# pid file. A lock held by a running process is refused; a lock whose process
# is gone (or with no pid file) is stale: it is cleared and taken.
update_take_lock() {
    local lock="$UPDATE_TARGET/.tingle-update.lock" pid attempt
    for attempt in 1 2; do
        if mkdir "$lock" 2>/dev/null; then
            UPDATE_LOCK="$lock"
            if ! printf '%s\n' "$$" > "$lock/pid"; then
                update_die "could not write the lock file '$lock/pid'"
            fi
            return 0
        fi
        pid=""
        if [ -f "$lock/pid" ]; then
            pid="$(cat "$lock/pid" 2>/dev/null || true)"
        fi
        case "$pid" in
            ''|*[!0-9]*) pid="" ;;
        esac
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            update_die "another update of '$UPDATE_TARGET' is in progress" \
                "(pid $pid holds '$lock'); nothing was changed"
        fi
        if [ "$attempt" -eq 2 ]; then
            break
        fi
        update_warn "clearing stale lock '$lock' (process" \
            "${pid:-unknown} is not running)"
        rm -rf "$lock"
    done
    update_die "could not take the lock '$lock'; nothing was changed"
}

# update_check_tingle_json
# Refuses (E3) a missing, unparsable or incomplete <target>/tingle.json, and
# saves its entries ("<hash>  <path>" lines) to $UPDATE_WORK/old_entries.
update_check_tingle_json() {
    local json="$UPDATE_TARGET/tingle.json"
    if [ ! -f "$json" ]; then
        update_die "'$json' not found; '$UPDATE_TARGET' is not a tingle" \
            "web install; nothing was changed"
    fi
    if ! tingle_json_check "$json" \
        || ! tingle_json_entries "$json" > "$UPDATE_WORK/old_entries"; then
        update_die "'$json' is corrupt (unparsable, or 'version', 'repo' or" \
            "'manifest' is missing); nothing was changed"
    fi
}

# update_check_incoming_manifest
# Refuses a missing, malformed or empty $SOURCE_ROOT/MANIFEST, so a broken
# release tree can never prune the whole install. Saves the new manifest as
# JSON ($UPDATE_WORK/new_manifest.json) and its paths ($UPDATE_WORK/new_paths).
update_check_incoming_manifest() {
    local manifest="$SOURCE_ROOT/MANIFEST"
    if [ ! -f "$manifest" ]; then
        update_die "the release tree has no MANIFEST ('$manifest');" \
            "nothing was changed"
    fi
    if ! tingle_manifest_to_json "$manifest" > "$UPDATE_WORK/new_manifest.json"; then
        update_die "'$manifest' is malformed; nothing was changed"
    fi
    if ! grep -q '[^[:space:]]' "$manifest"; then
        update_die "'$manifest' is empty; nothing was changed"
    fi
    grep '[^[:space:]]' "$manifest" | sed 's/^[^ ]*  //' > "$UPDATE_WORK/new_paths"
}

# update_check_edited
# E1: lists shipped files edited since install. A file is unedited when it
# is missing, or matches the old recorded hash or the incoming hash. Without
# recorded hashes, warns that edits will be overwritten.
update_check_edited() {
    local json="$UPDATE_TARGET/tingle.json" edited="$UPDATE_WORK/edited"
    local line hash path file current
    if ! tingle_json_tracks_hashes "$json"; then
        update_warn "'$json' records no file hashes (installed before 0.4.0" \
            "or by hand); local edits to shipped files cannot be detected" \
            "and will be overwritten"
        return 0
    fi
    : > "$edited"
    while IFS= read -r line || [ -n "$line" ]; do
        hash="${line%%  *}"
        path="${line#*  }"
        if ! path_is_safe "$path"; then
            update_warn "skipping unsafe manifest path '$path'"
            continue
        fi
        file="$UPDATE_TARGET/$path"
        if [ ! -e "$file" ] && [ ! -L "$file" ]; then
            continue
        fi
        if current="$(tingle_sha256 "$file" 2>/dev/null)"; then
            if [ "$current" = "$hash" ] \
                || grep -F -x -q -- "$current  $path" "$SOURCE_ROOT/MANIFEST"; then
                continue
            fi
        fi
        printf '%s\n' "$path" >> "$edited"
    done < "$UPDATE_WORK/old_entries"
    if [ ! -s "$edited" ]; then
        return 0
    fi
    if [ "${TINGLE_UPDATE_FORCE:-}" = "1" ]; then
        update_warn "overwriting locally edited shipped files" \
            "(TINGLE_UPDATE_FORCE=1):"
        sed 's/^/  /' "$edited" >&2
        return 0
    fi
    echo "installer.sh: these shipped files were edited locally:" >&2
    sed 's/^/  /' "$edited" >&2
    update_die "update aborted; nothing was changed. Re-run with" \
        "TINGLE_UPDATE_FORCE=1 (tingle update --force) to overwrite them"
}

# update_make_dirs <dir>
# mkdir -p <dir> inside the target, recording each directory it creates in
# $UPDATE_WORK/created_dirs so a failed stage can remove them again.
update_make_dirs() {
    local dir="$1" missing="" d="$1"
    while [ -n "$d" ] && [ ! -d "$d" ]; do
        missing="$d"$'\n'"$missing"
        d="${d%/*}"
    done
    if [ -z "$missing" ]; then
        return 0
    fi
    mkdir -p -- "$dir" || return 1
    printf '%s' "$missing" >> "$UPDATE_WORK/created_dirs"
}

# update_stage_one <path>
# Copies <source>/<path> (permissions kept) to its staged name in the target,
# overwriting any leftover from an earlier killed run.
update_stage_one() {
    local path="$1" staged
    staged="$(update_staged_name "$path")"
    if [ ! -f "$SOURCE_ROOT/$path" ]; then
        update_die "'$SOURCE_ROOT/$path' is listed in MANIFEST but missing" \
            "from the release tree; the install was left untouched"
    fi
    if ! update_make_dirs "${staged%/*}"; then
        update_die "could not create '${staged%/*}'; the install was left" \
            "untouched"
    fi
    printf '%s\n' "$staged" >> "$UPDATE_WORK/staged"
    rm -f -- "$staged"
    if ! cp -p -- "$SOURCE_ROOT/$path" "$staged"; then
        update_die "could not stage '$path' into '$UPDATE_TARGET'; the" \
            "install was left untouched"
    fi
}

# update_stage
# Phase 2: stages every safe path of the new MANIFEST, plus MANIFEST itself.
update_stage() {
    local path
    UPDATE_PHASE="stage"
    : > "$UPDATE_WORK/staged"
    : > "$UPDATE_WORK/created_dirs"
    while IFS= read -r path || [ -n "$path" ]; do
        if ! path_is_safe "$path"; then
            update_warn "skipping unsafe manifest path '$path'"
            continue
        fi
        update_stage_one "$path"
    done < "$UPDATE_WORK/new_paths"
    update_stage_one "MANIFEST"
}

# update_swap
# Phase 3: renames each staged file over its target (S2: never cp in
# place), with INT/TERM ignored for the duration.
update_swap() {
    local staged dir base
    trap '' INT TERM
    UPDATE_PHASE="swap"
    while IFS= read -r staged; do
        dir="${staged%/*}"
        base="${staged##*/}"
        base="${base#.}"
        base="${base%.tingle-new}"
        if ! mv -f -- "$staged" "$dir/$base"; then
            update_die "could not replace '$dir/$base'; re-run the update" \
                "to finish it"
        fi
    done < "$UPDATE_WORK/staged"
    trap 'exit 130' INT
    trap 'exit 143' TERM
}

# update_prune
# Phase 4: deletes the files of the old manifest that the new one no longer
# lists, then the directories they leave empty. Files in neither manifest
# (user-added) are never touched.
update_prune() {
    local line path file d
    UPDATE_PHASE="prune"
    if [ ! -s "$UPDATE_WORK/old_entries" ]; then
        update_warn "'$UPDATE_TARGET/tingle.json' has an empty manifest; stale" \
            "files from the previous version may be left behind"
        return 0
    fi
    while IFS= read -r line || [ -n "$line" ]; do
        path="${line#*  }"
        if ! path_is_safe "$path"; then
            update_warn "skipping unsafe manifest path '$path'"
            continue
        fi
        if grep -F -x -q -- "$path" "$UPDATE_WORK/new_paths"; then
            continue
        fi
        file="$UPDATE_TARGET/$path"
        rm -f -- "$(update_staged_name "$path")"
        if [ -d "$file" ] && [ ! -L "$file" ]; then
            update_warn "not removing '$file': it is now a directory"
            continue
        fi
        if [ -e "$file" ] || [ -L "$file" ]; then
            rm -f -- "$file" || update_warn "could not remove stale file '$file'"
        fi
        d="$path"
        while case "$d" in */*) true ;; *) false ;; esac; do
            d="${d%/*}"
            rmdir -- "$UPDATE_TARGET/$d" 2>/dev/null || break
        done
    done < "$UPDATE_WORK/old_entries"
}

# update_commit
# Phase 5: writes the new tingle.json last (temp file + rename), so until
# now the old one still describes the old version.
update_commit() {
    UPDATE_PHASE="commit"
    if ! write_tingle_json "$UPDATE_TARGET" \
        "$(cat "$UPDATE_WORK/new_manifest.json")"; then
        update_die "could not write '$UPDATE_TARGET/tingle.json'; re-run the" \
            "update to finish it"
    fi
}

update_main() {
    UPDATE_TARGET="$(normalize_target "$1")"
    trap update_on_exit EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM

    if ! command -v jq >/dev/null 2>&1; then
        update_die "update mode requires 'jq', which was not found on PATH"
    fi

    # Phase 1: preflight. Nothing changes except the lock.
    update_check_target
    update_take_lock
    UPDATE_WORK="$(mktemp -d "${TMPDIR:-/tmp}/tingle-update.XXXXXX")" \
        || update_die "could not create a scratch directory"
    update_check_tingle_json
    update_check_incoming_manifest
    update_check_edited


    update_stage
    update_swap
    update_prune
    update_commit
}
