# Guide Plan: code_check js_complexity: support .vue/.svelte/.astro single-file components

Main plan: [plan.md](plan.md)

## Shared contracts

- SFC rows look like any other row, under the component's own path, with
  original line numbers in `--details` and in the duplication output.
- Extraction errors show as `⛔ PARSE` with
  `Warning: cannot parse <file>: unsupported <script lang="coffee">` or
  `... : unterminated frontmatter`.

## Implementation Steps

### Step 1 — Guide updates
In `docs/guides/code_check/js_complexity.md`:
- **What it does** (around line 7): mention Vue, Svelte and Astro components.
- **File selection → Extensions** (around line 215): add `.vue .svelte
  .astro`, and a "Single-file components" subsection covering:
  - which blocks are analysed per framework;
  - `src=` and non-code `type=` blocks are skipped;
  - `lang` handling (Astro defaults to TS);
  - several blocks are combined into one score;
  - `<template>`/`<style>` are never analysed;
  - line numbers are the original ones.
- **Files shown as `OK 0.0`** (around line 801): add components with no
  script.
- **Parse warnings** (around line 817): add the two extraction-error messages.
- **Examples:** add one `.vue` row, ideally with `--details` showing an
  original line number.

## Files to Change
- `docs/guides/code_check/js_complexity.md` — the SFC documentation.
