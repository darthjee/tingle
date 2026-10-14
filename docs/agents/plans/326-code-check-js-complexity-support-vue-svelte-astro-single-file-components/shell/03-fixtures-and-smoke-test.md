# Fixtures and smoke test

Add the fixtures from spec `sfc.md`, section 7, to
`docker/js_complexity/fixture/`:

- `NoScript.vue` (template only);
- `TwoBlocks.vue`: `<script>` + `<script setup lang="ts">`, with at least one
  function in each block;
- `External.vue`: only `<script src="./external.js"></script>`;
- `Coffee.vue`: `<script lang="coffee">`;
- `Counter.svelte`: `<script context="module">` + `<script lang="ts">`;
- `Page.astro`: frontmatter + `<script>`, with functions in both;
- `Cart.vue.ts`, next to `Cart.vue`.

Fixture content must not create jscpd duplication with the existing fixtures
(`dup_a.js`/`dup_b.js`), unless an assertion expects it.

Update `smoke_test_js_complexity` in `scripts/release_image.sh`:

- add the new files to the fixture list;
- `Cart.vue` is no longer refused. Assert a normal row: `fta.score` between
  25 and 40, `fta.lines` 11, `duplication.lines` 0, and one function at
  `line` 13. Remove it from the "refused" loop at line ~782 and update the
  comment at line ~576;
- `NoScript.vue` and `External.vue`: `parse_error` false, `fta` null,
  `duplication.lines` 0, `functions` `[]`, and no warnings;
- `Coffee.vue`: `parse_error` true, plus an `entrypoint` warning
  `unsupported <script lang="coffee">`;
- `TwoBlocks.vue`, `Counter.svelte` and `Page.astro`: normal rows. For
  `TwoBlocks.vue` and `Page.astro`, assert that the function lines equal the
  lines in the original file;
- `Cart.vue.ts`: a separate normal row, distinct from `Cart.vue`.

## Files to Change
- `docker/js_complexity/fixture/NoScript.vue`, `TwoBlocks.vue`,
  `External.vue`, `Coffee.vue`, `Counter.svelte`, `Page.astro`,
  `Cart.vue.ts` — new fixtures.
- `scripts/release_image.sh` — the fixture list and the SFC assertions in
  `smoke_test_js_complexity`.
