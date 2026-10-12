# Fixture
Create `docker/js_complexity/fixture/` with **every** file in the `image.md` §9 table, even though some expectations only apply from #324, #325 or #326:

`simple.js`, `complex.ts` (~260 lines, score > 60, a `reducer`, a `Store` class, no `<T>value` assertions), `component.tsx`, `widget.jsx`, `dup_a.js`/`dup_b.js` (the same 20-line body at different offsets), `broken.js`, `empty.js` (0 bytes), `short.js`, `bundle.min.js`, `build/out.js`, `ext/a.mjs`, `ext/b.cjs`, `ext/c.mts`, `ext/d.cts`, `ext/UPPER.JS`, `ext/types.d.ts`, `crlf.js` (CRLF endings), `bom.ts` (UTF-8 BOM), `latin1.js` (ISO-8859-1 bytes), `Cart.vue` (`<script setup lang="ts">` with a `computed` on lines 8–21).

Make sure git keeps the bytes: CRLF in `crlf.js`, the BOM in `bom.ts` and Latin-1 in `latin1.js`. Add a `docker/js_complexity/fixture/.gitattributes` with `* -text` (or per-file `-text`) if needed, and check with `git diff --cached` / `xxd`.

Tune the content so FTA 3.1.0 gives the expected results from §9 and §10. Close to the grounding numbers is enough; the §9 assertions are thresholds and states, not exact scores.

## Files to Change
- `docker/js_complexity/fixture/**` — new.
