# Shell Plan: code_check js_complexity: remove docs/agents/specs/code_check/js_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

- Point every comment to `docs/agents/tingle-js-complexity-image.md` using
  the mapping table in [plan.md](plan.md#shared-contracts). Name the heading
  in words, not a section number.
- Do this after product-owner step 01 (the target sections must exist).
  Comments only: no code change.

## Implementation Steps

### Step 1 — Repoint the docker/js_complexity/ comments
- `Dockerfile` (lines 23-24): `See docs/agents/tingle-js-complexity-image.md
  ("Bumping versions") for the bump procedure.`
- `entrypoint.js` (lines 50-53): replace the four spec paths with
  `Contract: docs/agents/tingle-js-complexity-image.md ("Contract").`
- `lib/staging.js` (line 11) and `lib/sfc.js` (line 4): point to
  `docs/agents/tingle-js-complexity-image.md ("Single-file components")`.
- `lib/jscpd.js` (line 4) and `lib/escomplex.js` (line 4): point to
  `docs/agents/tingle-js-complexity-image.md ("Contract")`.

### Step 2 — Repoint the release_image.sh smoke-test comment
`scripts/release_image.sh` (lines 562-582): the comment above the
js_complexity smoke-test function names `image.md` section 9,
`duplication.md` section 6, `details.md` section 8 and `sfc.md` section 7.
Point it once to `docs/agents/tingle-js-complexity-image.md ("Smoke test")`
and keep the summary of what is checked.

## Files to Change
- `docker/js_complexity/Dockerfile` — bump-procedure comment.
- `docker/js_complexity/entrypoint.js` — contract comment.
- `docker/js_complexity/lib/staging.js`, `lib/sfc.js`, `lib/jscpd.js`, `lib/escomplex.js` — header comments.
- `scripts/release_image.sh` — smoke-test comment.

## CI Checks
- `scripts/release_image.sh`: `bash -n scripts/release_image.sh`.
- `docker/js_complexity/`: no test script; `node --check` on each edited `.js` file.

## Notes
- Do not rebuild or re-release the image: nothing the image does changes.
