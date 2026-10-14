# SFC extraction module

Add `docker/js_complexity/lib/sfc.js`, a pure function module with no file
system access, so it is easy to reason about and to exercise from the smoke
test:

- `extractSfc(text, ext)` returns either `{ error: "<message>" }` or
  `{ code, vext }`:
  - strip an optional leading BOM (it becomes a space, so it does not shift
    columns, and it stays on line 1);
  - for `astro`, if the first line is exactly `---`, the frontmatter runs to
    the next line that is exactly `---`. With no closing fence, return
    `{ error: "unterminated frontmatter" }`. The frontmatter content is kept
    as TS;
  - find every `<script\b[^>]*>` (case-insensitive) and its content up to the
    first following `</script\s*>`. Parse the attributes of the opening tag
    (`src`, `type`, `lang`; quoted or bare values, case-insensitive names);
  - skip the block if it has `src`, or a `type` other than `module`,
    `text/javascript` or `application/javascript`;
  - map `lang` to JS / JSX / TS / TSX as in spec `sfc.md`, section 2. Any
    other value returns `{ error: 'unsupported <script lang="<lang>">' }`.
    A missing `lang` is JS for vue/svelte and TS for astro;
  - build `code`: the original text with every character outside the kept
    block contents replaced by a space, and line terminators kept;
  - `vext` is `tsx` / `ts` / `jsx` / `js`, depending on whether any kept block
    is TS and whether any is JSX.
- `SFC_EXTENSIONS = new Set(["vue", "svelte", "astro"])`, exported.

Follow the style of the other `lib/*.js` files: `"use strict"`, a header
comment pointing at `docs/agents/specs/code_check/js_complexity/sfc.md`, and
small named functions. Keep it under the repo's complexity thresholds.

## Files to Change
- `docker/js_complexity/lib/sfc.js` — new: block detection, attribute
  parsing, language resolution and padding.
- `docker/js_complexity/Dockerfile` — only if `lib/` files are copied one by
  one rather than as a directory. Check this.
