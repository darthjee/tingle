#!/usr/bin/env bash
#
# update.sh - Sourced helper library holding install/installer.sh's update
# mode. The behaviour (trigger, env vars, lock, phases, safety rules and
# recovery) is documented in the header of install/installer.sh.
#
# This file only defines functions: it sets no shell options and runs
# nothing when sourced. It relies on the globals and helpers installer.sh
# defines before calling update_main (REPO, VERSION, SOURCE_ROOT,
# path_is_safe, write_tingle_json) and on install/manifest.sh.
#
# Functions:
#
#   update_main <target>
#     Runs every update phase against the normalized, absolute install
#     folder <target>. Exits non-zero on any refusal or failure.
#

update_main() {
    local target="$1"
    echo "installer.sh: update mode for '$target' is not implemented yet" >&2
    return 1
}
