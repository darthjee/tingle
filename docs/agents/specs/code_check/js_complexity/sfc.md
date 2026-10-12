# Spec: `.vue`, `.svelte` and `.astro` support

Sub-issue: #326. Parent: #315. Shared contracts: [README.md](README.md).

None of the three tools reads single-file components (SFCs) the way tingle
needs, so the image's entrypoint **extracts the script part** of each SFC
into a virtual module, and the three tools analyse that module like any
other file. #326 changes the image and the Python selection in the same PR,
after #324 and #325, so the extracted scripts feed FTA, jscpd and escomplex.
The `<template>` markup and the styles are never analysed.

## 1. Selection (host)

- `SFC_EXTENSIONS = [".vue", ".svelte", ".astro"]` is added to the extension
  list passed to `select_files` (case-insensitive, like the core list). See
  [file-selection.md](file-selection.md#2-extensions-and-skip-rules).
- No skip rule applies to SFCs. The default excludes, `.gitignore`, the
  globs and the symlink rule apply as for any file.
- The help texts, the guide and `long_help` mention the three extensions.

## 2. Extraction (image)

The entrypoint accepts `vue`, `svelte` and `astro` as extensions from #326
on (until then they are refused as `unsupported extension`; see
[image.md](image.md#4-entrypoint-input)). It reads the file as UTF-8 (a file
that is not valid UTF-8 is a `PARSE` file, as for any other file), then
finds the **script blocks**:

| Kind | Blocks |
|------|--------|
| `.vue` | every `<script ...>...</script>` element: `<script>` and `<script setup>` |
| `.svelte` | every `<script ...>...</script>` element: `<script>`, `<script context="module">` and `<script module>` |
| `.astro` | the frontmatter, then every `<script ...>...</script>` element |

- A `<script>` element is an opening tag matching `<script\b[^>]*>`
  (case-insensitive), and its content runs to the first following
  `</script\s*>`. HTML comments and `<template>` contents are not
  special-cased.
- The **Astro frontmatter** is present when the file's first line (after an
  optional BOM) is exactly `---`. Its content runs to the next line that is
  exactly `---`. A first line `---` with no closing fence is an extraction
  error (section 6).
- A `<script>` with a `src` attribute is **skipped**: the external file is
  analysed on its own when it is selected.
- A `<script>` with a `type` attribute other than `module`,
  `text/javascript` or `application/javascript` (case-insensitive) is
  skipped: it is data (for example `application/ld+json`), not code.

**Language of a block.** From its `lang` attribute, case-insensitive:

| `lang` | Language |
|--------|----------|
| absent, `js`, `javascript` | JS |
| `jsx` | JS + JSX |
| `ts`, `typescript` | TS |
| `tsx` | TS + JSX |
| anything else (for example `coffee`) | unsupported: extraction error (section 6) |

The Astro frontmatter and Astro `<script>` blocks without `lang` are TS
(Astro compiles both as TypeScript).

## 3. Virtual module

All kept blocks of a file are **combined into one virtual module**, in file
order. The file is analysed once, so it gets one FTA score, one cyclo, one
set of duplication ranges and one set of functions. Per-block results are
never summed: FTA and Halstead scores are not additive.

- **Language:** TS if **any** block is TS; JSX if any block is JSX. The
  virtual module's extension is `tsx` (TS and JSX), `ts` (TS), `jsx` (JSX)
  or `js` (neither).
- **Staging:** `/tmp/stage/sfc/<n>.<ext>.<vext>`, with `<n>` the input line
  number, `<ext>` the SFC extension (lower-cased) and `<vext>` the virtual
  module's extension, for example `/tmp/stage/sfc/5.vue.ts`. The `sfc/`
  subtree is separate from `plain/`, so a real `Cart.vue.ts` (staged as
  `plain/<m>.ts`) and the virtual module of `Cart.vue` never collide. Both
  map back to their own input line.
- A file whose kept blocks are all empty, or that has no kept block, is still
  staged, as a module with no code (section 6).

## 4. Line map

The line map is the identity: the virtual module **keeps the original line
numbers** (README deviation 10).

- The virtual module is the original text with **every character outside
  the kept script contents replaced by a space**, and every line terminator
  (`\r\n`, `\n`, `\r`) kept as it is. Tags, markup, styles, skipped blocks,
  the Astro `---` fences and a leading BOM all become spaces.
- Line `L` of the virtual module is therefore line `L` of the original
  file, so FTA, jscpd and escomplex report original line numbers directly.
  `--details` line numbers and jscpd ranges need no offset.
- FTA removes blank lines before counting and parsing, so the padding does
  not change its results. Grounding: for `Cart.vue`, the padded virtual
  module and the bare script gave the same FTA result (score `30.66`, cyclo
  3, `line_count` 11), and escomplex reported the `computed` callback at
  line 13 of `Cart.vue` (line 6 of the bare script). The same file with CRLF
  line endings and a BOM gave line 13 too.

## 5. Mapping back

The tools report `sfc/<n>.<ext>.<vext>`; the entrypoint parses `<n>` and
writes the results on the `files` entry of input line `<n>`, whose `path` is
the original `Cart.vue` line. FTA's `Failed to analyze /tmp/stage/sfc/<n>…`
log lines map the same way, so a syntax error in a script block makes the
SFC a `PARSE` row. Tingle needs no SFC-specific code beyond the extension
list.

## 6. Edge cases

| Case | Result |
|------|--------|
| No `<script>` (template-only component), or only skipped blocks | Staged with no code: FTA drops it → `fta: null`, `parse_error: false` → `OK`, score 0. `duplication: {"lines": 0}`, `functions: []`. |
| Several script blocks (`<script>` + `<script setup>`, `context="module"` + instance script, frontmatter + `<script>`) | One combined virtual module (section 3). |
| `<script src="...">` | That block is skipped; the external file is analysed on its own if selected. |
| Unknown `lang` (for example `coffee`) | Extraction error: `parse_error: true`, not staged, warning `{"tool": "entrypoint", "path": <line>, "message": "unsupported <script lang=\"coffee\">"}` → `⛔ PARSE` row with `Warning: cannot parse <file>: unsupported <script lang="coffee">`. |
| Astro frontmatter with no closing `---` | Extraction error, message `unterminated frontmatter` → `⛔ PARSE`. |
| A syntax error in a script block | FTA's parse failure → `⛔ PARSE` (section 5). |
| Two blocks both declaring the same name (for example the same `import` in `<script>` and `<script setup>`) | Analysed as one module. If a tool rejects the duplicate declaration, the usual rules apply: FTA → `PARSE`; escomplex only → `(per-function data unavailable)` under `--details`. |
| `<template>` and `<style>` | Never analysed. |
| Not valid UTF-8 | `PARSE`, as for any file. |

## 7. Smoke test, docs and tests

- The smoke test sends `Cart.vue` and asserts a normal row: `fta.score`
  between 25 and 40, `fta.lines` 11, `duplication.lines` 0, and one function
  at `line` 13. #326 adds to `docker/js_complexity/fixture/`:
  - `NoScript.vue` (template only): `fta: null`, `parse_error: false`;
  - `TwoBlocks.vue` (`<script>` + `<script setup lang="ts">`): a normal row,
    functions from both blocks with their original lines;
  - `External.vue` (`<script src="./external.js">` only): like `NoScript.vue`;
  - `Coffee.vue` (`<script lang="coffee">`): `parse_error: true` and the
    `entrypoint` warning;
  - `Counter.svelte` (`<script context="module">` + `<script lang="ts">`):
    a normal row;
  - `Page.astro` (frontmatter + `<script>`): a normal row, functions with
    their original lines;
  - `Cart.vue.ts` next to `Cart.vue`: two separate normal rows.
- Docs: the extensions and the SFC rules in
  `docs/guides/code_check/js_complexity.md`, `long_help`, and
  `docs/agents/tingle-js-complexity-image.md`.
- Python tests: `.vue/.svelte/.astro` selected in any case; SFC rows mapped
  back to the original path.
