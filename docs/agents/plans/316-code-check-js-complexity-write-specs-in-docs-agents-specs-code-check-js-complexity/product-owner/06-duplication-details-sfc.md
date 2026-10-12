# duplication.md, details.md, sfc.md
**`docs/agents/specs/code_check/js_complexity/duplication.md`** (#324) covers:
- the jscpd invocation on the staged tree, with the **pinned `min-tokens`/`min-lines`/formats**;
- the per-file duplicated-lines computation (each line counted once, across all clones);
- `duplication: {"lines": N}` in the merged JSON;
- the `Dup` column (`-` for `null`, `0` for 0);
- comparison within the selection only;
- failure handling: degrade, add a `warnings` entry, print a `Warning:` with the exact text, and leave the exit code unchanged.

**`docs/agents/specs/code_check/js_complexity/details.md`** (#325) covers:
- the escomplex wrapper and the **pinned parser options**;
- `functions: [{name, line, cyclo, sloc}]`;
- `--details [N]` (default 5, 0 means all, never under `PARSE`), mirroring `rubycritic --details`;
- the `(per-function data unavailable)` note when `functions` is `null` and FTA parsed the file;
- a crash degrading with one warning;
- the `details` config key;
- correct line numbers with CRLF and BOM.

**`docs/agents/specs/code_check/js_complexity/sfc.md`** (#326) covers:
- extraction for `.vue`/`.svelte` (`<script>`, `<script setup>`, `<script context="module">`) and for `.astro` (the frontmatter plus `<script>`);
- **combining all blocks into one virtual module** in file order, treated as TS if any block is TS, and staged in `/tmp/stage-sfc/`;
- the line map back to the original file;
- the edge cases: no script, `src=` blocks, an unknown `lang` (`PARSE`), and `<template>` never analysed;
- the mapping back to the original path.

## Files to Change
- `docs/agents/specs/code_check/js_complexity/duplication.md` — new.
- `docs/agents/specs/code_check/js_complexity/details.md` — new.
- `docs/agents/specs/code_check/js_complexity/sfc.md` — new.
