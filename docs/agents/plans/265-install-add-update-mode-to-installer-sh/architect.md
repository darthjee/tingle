# Architect Plan: install: add update mode to installer.sh

Main plan: [plan.md](plan.md)

## Shared contracts

Implement exactly the env vars in [plan.md](plan.md#shared-contracts):
`TINGLE_UPDATE_TARGET`, `TINGLE_UPDATE_FORCE`, `TINGLE_UPDATE_CLEANUP`,
`TINGLE_REPO`, `TINGLE_VERSION`, plus the lock path, staged-file naming,
`MANIFEST` swap, incoming-`MANIFEST` refusal and unsafe-path rule listed
there. The first-install path (no `TINGLE_UPDATE_TARGET`) must behave
exactly as today and keep ending with `exec "$target/bin/tingle" install`.

## Steps

- [01 — Restructure installer and add the update-mode trigger](architect/01-trigger-and-structure.md)
- [02 — Preflight: lock, checks and edited-file detection](architect/02-preflight.md)
- [03 — Stage, swap, prune and commit](architect/03-stage-swap-prune-commit.md)
- [04 — Wire, cleanup and header comment](architect/04-wire-cleanup-header.md)
- [05 — Manual verification](architect/05-manual-verification.md)

## CI Checks
- There is no CI job covering `install/`; run `shellcheck install/*.sh`
  locally.

## Notes
- Reuse `install/manifest.sh` (#264) instead of re-implementing hashing or
  `tingle.json` parsing: `tingle_sha256`, `tingle_manifest_to_json`,
  `tingle_json_check`, `tingle_json_entries`, `tingle_json_tracks_hashes`.
  Split `MANIFEST` / `tingle_json_entries` lines on the **first two spaces
  only** (paths may contain spaces).
- Keep the script bash-3.2 compatible (macOS default bash): no associative
  arrays, no `mapfile`. Use temp files plus `grep -F -x` / `awk` lookups for
  "is this path in the new manifest" checks.
- `jq` is required only in update mode; the first-install path stays
  jq-optional.
- Traps: the stage trap must remove staged files **and** the lock (and the
  source tree when `TINGLE_UPDATE_CLEANUP=1`). The swap phase ignores
  `INT`/`TERM`. Under `set -e`, make sure a failing check inside a function
  does not skip the cleanup trap (`trap … EXIT`).
- If the file grows large, it is acceptable to move update-mode functions
  into a sibling sourced file (e.g. `install/update.sh`) listed in the header,
  as long as it ships in the release zip (`install/` is already in
  `INCLUDES`).
