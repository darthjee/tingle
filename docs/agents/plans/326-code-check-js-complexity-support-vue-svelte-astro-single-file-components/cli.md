# Cli Plan: code_check js_complexity: support .vue/.svelte/.astro single-file components

Main plan: [plan.md](plan.md)

## Shared contracts

- The host analyses `.vue`, `.svelte` and `.astro` (any letter case) in
  addition to `.js .mjs .cjs .jsx .ts .mts .cts .tsx`. Only their `<script>`
  blocks and the Astro frontmatter are analysed.

## Implementation Steps

### Step 1 — long_help
In `commands/python.json`, `code_check` → `long_help`, js_complexity's
"File selection" section: extend the paragraph that starts
"Files with the extensions .js, .mjs, ...". Add that `.vue`, `.svelte` and
`.astro` single-file components are analysed too, by their `<script>` blocks
and Astro frontmatter only; that line numbers are the original ones; and that
a component with no script shows as OK 0. Keep the 80-column wrapping used in
that string.

## Files to Change
- `commands/python.json` — the js_complexity long_help extension paragraph.

## Notes
- If `python/tests/code_check/test_completion.py` or a help snapshot test
  asserts on this text, update it together with the python agent.
