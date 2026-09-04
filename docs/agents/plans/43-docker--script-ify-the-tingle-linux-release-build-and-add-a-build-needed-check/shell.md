# shell Plan: Docker: script-ify the tingle-linux release build and add a build-needed check

Main plan: [plan.md](plan.md)

## Shared contracts

- Owns/creates `shell/linux/VERSION` — the single source of truth
  `architect`'s `scripts/release_image.sh` reads/validates and this same
  agent's `docker_run.sh` reads. See [plan.md](plan.md)'s
  `## Shared contracts` for the full file-format contract.

## Implementation Steps

### Step 1 — Add shell/linux/VERSION

Create `shell/linux/VERSION`, a single line containing exactly `v0.0.1`
(the seed value decided during issue enhancement — preserves continuity
with the existing, never-actually-published `0.0.1` placeholder, corrected
to the `v`-prefixed convention CI actually produces). No trailing content
beyond the tag itself.

### Step 2 — Read the pin from docker_run.sh

In `shell/linux/docker_run.sh`, replace the hardcoded:

```bash
TINGLE_LINUX_IMAGE="darthjee/tingle:0.0.1"
```

with a read from the new pin file, e.g.:

```bash
TINGLE_LINUX_IMAGE="darthjee/tingle:$(cat "$(dirname "${BASH_SOURCE[0]}")/VERSION")"
```

(Resolve `VERSION` relative to `docker_run.sh`'s own directory rather than
the caller's cwd, since this file is sourced, not executed directly — see
its own header comment for the sourcing convention.) Keep everything else
in the file (the `docker_run` function, its mode handling) unchanged.

## Files to Change
- `shell/linux/VERSION` (new) — seed value `v0.0.1`.
- `shell/linux/docker_run.sh` — read `TINGLE_LINUX_IMAGE` from `VERSION`
  instead of the hardcoded string.

## Notes
- No test suite currently covers `shell/linux/`; verify by sourcing
  `docker_run.sh` and checking `$TINGLE_LINUX_IMAGE` resolves to
  `darthjee/tingle:v0.0.1`.
