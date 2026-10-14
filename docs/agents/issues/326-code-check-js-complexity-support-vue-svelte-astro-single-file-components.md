# Issue: code_check js_complexity: support .vue/.svelte/.astro single-file components

## Description
Support Vue, Svelte and Astro single-file components (`.vue`, `.svelte`, `.astro`) in `tingle code_check js_complexity` (parent #315). The image's entrypoint extracts the script part of each SFC into a virtual module, which FTA, jscpd and escomplex then analyse like any other file.

Spec: `docs/agents/specs/code_check/js_complexity/sfc.md` (the spec is authoritative where this issue is less precise).

## Problem
Most front-end logic in Vue, Svelte and Astro projects lives inside SFCs, which FTA, jscpd and escomplex cannot parse natively. Today the host never selects these files, and the image refuses them as `unsupported extension`, so they are missing from the report.

## Expected Behavior
### Selection (host, Python)
- `SFC_EXTENSIONS = [".vue", ".svelte", ".astro"]` is added to the extensions passed to `select_files`, matched case-insensitively.
- No extra skip rule applies. Default excludes, `.gitignore`, globs and the symlink rule apply as for any file.
- The help texts and `long_help` mention the three extensions.

### Extraction (image entrypoint)
- The entrypoint accepts `vue`, `svelte` and `astro`. It reads the file as UTF-8; a file that is not valid UTF-8 is a `PARSE` row.
- Script blocks:
  - `.vue`: every `<script ...>...</script>` (`<script>`, `<script setup>`);
  - `.svelte`: every `<script ...>...</script>` (`<script>`, `<script context="module">`, `<script module>`);
  - `.astro`: the `---` frontmatter (first line, after an optional BOM, is exactly `---`, closed by the next `---` line), then every `<script>` block.
- A block opens at `<script\b[^>]*>` (case-insensitive) and ends at the first `</script\s*>`.
- Skipped blocks:
  - `src="..."` blocks, because the external file is analysed on its own if it is selected;
  - blocks whose `type` is not `module`, `text/javascript` or `application/javascript`, for example `application/ld+json`.
- Language comes from `lang`, case-insensitive:
  - absent, `js` or `javascript` → JS;
  - `jsx` → JSX;
  - `ts` or `typescript` → TS;
  - `tsx` → TS + JSX;
  - anything else → extraction error.
  - Astro blocks without `lang` (frontmatter and `<script>`) are TS.

### Virtual module
- All kept blocks of a file are combined into **one** virtual module, in file order. The file gets one score, one cyclo, one set of duplication ranges and one set of functions. Results are never summed per block.
- The virtual module is TS if any block is TS and JSX if any block is JSX. Its extension is `tsx`, `ts`, `jsx` or `js`.
- It is staged as `/tmp/stage/sfc/<n>.<ext>.<vext>` (for example `sfc/5.vue.ts`). This is a separate subtree from `plain/`, so `Cart.vue` and a real `Cart.vue.ts` never collide.
- **Line map is the identity.** Every character outside the kept script contents (tags, markup, styles, skipped blocks, the Astro fences, the BOM) is replaced by a space, and line terminators are kept. Line numbers from FTA, jscpd and escomplex are therefore already the original ones, and `--details` and duplication ranges need no offset.
- Tool output for `sfc/<n>...` is mapped back to input line `<n>`, including FTA's `Failed to analyze` lines, so a syntax error in a block makes the SFC a `PARSE` row.

### Edge cases
- No script, or only skipped blocks: staged with no code → `fta: null`, `parse_error: false` → `OK`, score 0, `duplication.lines` 0, no functions.
- Unknown `lang` (for example `coffee`): not staged, `parse_error: true`, warning `unsupported <script lang="coffee">` from `entrypoint` → `⛔ PARSE` row.
- Astro frontmatter without a closing `---`: extraction error `unterminated frontmatter` → `⛔ PARSE`.
- Two blocks declaring the same name: analysed as one module. If FTA rejects it, the row is `PARSE`. If only escomplex rejects it, `--details` shows `(per-function data unavailable)`.
- `<template>` and `<style>` are never analysed.

### Tests and docs
- New smoke-test fixtures in `docker/js_complexity/fixture/`, next to the existing `Cart.vue`:
  - `NoScript.vue`;
  - `TwoBlocks.vue`;
  - `External.vue`;
  - `Coffee.vue`;
  - `Counter.svelte`;
  - `Page.astro`;
  - `Cart.vue.ts`.

  The expected results are listed in spec section 7. The existing `Cart.vue` check asserts a normal row with its function at line 13.
- Python tests:
  - `.vue`, `.svelte` and `.astro` are selected in any letter case;
  - SFC rows are mapped back to the original path.
- Docs to update:
  - `docs/guides/code_check/js_complexity.md`;
  - `long_help`;
  - `docker/js_complexity/DOCKERHUB_DESCRIPTION.md`;
  - `docs/agents/tingle-js-complexity-image.md`.

## Solution
Change the image and the Python side **in the same PR**, so the extracted scripts feed all three tools as soon as the host starts selecting SFCs. The dependencies, #324 (jscpd duplication) and #325 (`--details` via escomplex), are already merged.

### Agents
- `shell`: the SFC extraction, staging and mapping-back in the image (`docker/js_complexity/`, including `lib/selection.js`, `lib/staging.js` and the escomplex wrapper), plus the fixtures and the smoke test.
- `python`: `SFC_EXTENSIONS` in `python/code_check/js_complexity/`, the help texts, `long_help`, and the tests.
- `guide`: `docs/guides/code_check/js_complexity.md`.
- `product-owner`: `docs/agents/tingle-js-complexity-image.md`.

## Benefits
- Covers the logic of modern front-end frameworks, not just plain JS/TS files.
- Line numbers in `--details` and in the duplication ranges point straight into the original component, with no offset arithmetic.
