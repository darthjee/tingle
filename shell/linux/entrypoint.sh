#!/bin/sh
#
# entrypoint.sh - Image entrypoint for the `tingle linux` toolbox image.
#
# Installed as /usr/local/bin/tingle-entrypoint (mode 0755) and set as the
# image ENTRYPOINT; CMD defaults to `bash`.
#
# `tingle linux` runs containers as the host uid:gid (e.g. 501:20 on macOS),
# which usually has no entry in the image's /etc/passwd. Without one, HOME
# falls back to `/` and ssh aborts with "No user exists for uid ...". Making
# /etc/passwd writable would let any process add a uid-0 entry, so instead:
#
#   - HOME is always /home/tingle (mode 1777 in the image);
#   - when `id -un` fails, a private copy of /etc/passwd (plus a
#     `tingle-host` entry for the current uid) and of /etc/group (plus a
#     `tingle-host` group, only when the gid has none) is written to a
#     mktemp dir, and libnss_wrapper is LD_PRELOADed to serve it. The
#     library path is found at runtime, so this works on amd64 and arm64;
#   - when ~/.ssh/host_config exists (the host ~/.ssh/config, mounted there
#     by callers) and ~/.ssh/config doesn't, a wrapper config is written that
#     ignores macOS-only options (UseKeychain, AddKeysToAgent) and includes
#     it.
#
# Every step is best effort: if the library or a temp dir is unavailable,
# or a write fails, the step is skipped silently. The script never prints
# to stdout (so pipelines such as `tingle linux sed` are unaffected) and
# always ends with `exec "$@"`. For that reason it deliberately does not use
# `set -e`.
#
# Usage:
#   tingle-entrypoint <command> [args...]
#
# Dependencies: POSIX sh, coreutils (id, mktemp, cat, head), findutils,
#   getent (libc-bin), libnss-wrapper.
#
set -u

export HOME=/home/tingle

if ! id -un >/dev/null 2>&1; then
    lib=$(find /usr/lib -maxdepth 2 -name libnss_wrapper.so 2>/dev/null | head -n 1)
    dir=$(mktemp -d 2>/dev/null) || dir=""
    if [ -n "$lib" ] && [ -n "$dir" ]; then
        uid=$(id -u)
        gid=$(id -g)
        if {
            cat /etc/passwd &&
                echo "tingle-host:x:$uid:$gid::$HOME:/bin/bash"
        } >"$dir/passwd" 2>/dev/null &&
            {
                cat /etc/group &&
                    { getent group "$gid" >/dev/null || echo "tingle-host:x:$gid:"; }
            } >"$dir/group" 2>/dev/null; then
            export LD_PRELOAD="$lib" NSS_WRAPPER_PASSWD="$dir/passwd" NSS_WRAPPER_GROUP="$dir/group"
        fi
    fi
fi

if [ -f "$HOME/.ssh/host_config" ] && [ ! -e "$HOME/.ssh/config" ]; then
    {
        printf 'IgnoreUnknown UseKeychain,AddKeysToAgent\nInclude ~/.ssh/host_config\n' \
            >"$HOME/.ssh/config"
    } 2>/dev/null
fi

exec "$@"
