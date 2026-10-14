# Product-owner Plan: code_check js_complexity: support .vue/.svelte/.astro single-file components

Main plan: [plan.md](plan.md)

## Shared contracts

- The image accepts `vue`, `svelte` and `astro`, extracts the script blocks
  into a padded virtual module at `/tmp/stage/sfc/<n>.<ext>.<vext>`, and keeps
  the original line numbers.
- Extraction errors produce `parse_error: true` plus an `entrypoint` warning.
- The JSON shape is unchanged.

## Implementation Steps

### Step 1 — Image doc and architecture
- `docs/agents/tingle-js-complexity-image.md`:
  - in **Contract**, document the accepted SFC extensions, the extraction
    rules, the `sfc/` staging and the padding/identity line map, and the two
    new `entrypoint` warning messages. Summarise and link to spec `sfc.md`
    while the spec still exists; this doc is what remains after #327 removes
    the specs, so it must be self-sufficient;
  - in **Smoke test** (around lines 441–505), change the `Cart.vue` row from
    "refused (until #326)" to a normal row, add the new fixtures and their
    expectations, and drop the "added by #326" note.
- `docs/agents/architecture.md` (around line 243): add `SFC_EXTENSIONS` next
  to `EXTENSIONS` in the js_complexity constants description.

## Files to Change
- `docs/agents/tingle-js-complexity-image.md` — the SFC contract and the
  smoke-test fixtures.
- `docs/agents/architecture.md` — the `SFC_EXTENSIONS` constant.

## Notes
- Do not edit `docs/agents/specs/code_check/js_complexity/`. The spec is
  already final for #326, and #327 removes it.
