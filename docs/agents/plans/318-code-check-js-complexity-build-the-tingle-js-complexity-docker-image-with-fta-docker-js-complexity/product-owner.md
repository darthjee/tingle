# Product-owner Plan: code_check js_complexity: build the tingle_js_complexity Docker image with FTA (docker/js_complexity/)

Main plan: [plan.md](plan.md)

## Shared contracts

- `docker/js_complexity/` builds `tingle_js_complexity` (published later as `darthjee/tingle_js_complexity`, #319). It is owned by the `shell` agent.

## Implementation Steps

### Step 1 — List `docker/js_complexity/` in the folder structure
In `docs/agents/folder-structure.md`, extend the `docker/` row so that it names both images: `docker/rubycritic/` builds `tingle_rubycritic` (keep the existing link), and `docker/js_complexity/` builds `tingle_js_complexity`. For the new image, link the spec [`specs/code_check/js_complexity/image.md`](../../specs/code_check/js_complexity/image.md) for now. #319 adds `docs/agents/tingle-js-complexity-image.md` and repoints the link. Keep "Owned by the `shell` agent."

## Files to Change
- `docs/agents/folder-structure.md` — the `docker/` row mentions `docker/js_complexity/`.

## Notes
- Do not create `docs/agents/tingle-js-complexity-image.md`; that is #319's job (`release.md` §6).
- Do not touch the specs.
