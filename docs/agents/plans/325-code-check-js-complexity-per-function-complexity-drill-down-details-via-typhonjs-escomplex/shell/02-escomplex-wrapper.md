# Write the escomplex wrapper
Create `docker/js_complexity/lib/escomplex.js`, a standalone script (`node /opt/tingle_js_complexity/lib/escomplex.js`):
- It reads a JSON array of staged paths on stdin and writes one JSON object on stdout, mapping each path to `{"functions": [...]}` or `{"error": "<one-line message>"}`.
- It reads each file as UTF-8 and calls `escomplex.analyzeModule(source, MODULE_OPTIONS, { sourceType: "unambiguous", plugins })`, catching exceptions per file.
- `MODULE_OPTIONS = { logicalor: true, switchcase: true, forin: false, trycatch: false, newmi: false }`.
- `plugins` come from the last extension: `ts`/`mts`/`cts` → `["typescript", ...COMMON]`, `tsx` → `["typescript", "jsx", ...COMMON]`, and `js`/`mjs`/`cjs`/`jsx` → `["jsx", ...COMMON]`. `COMMON` is the list in spec §2.
- It flattens `methods` and `classes[].methods` into `{name, line: lineStart, cyclo: cyclomatic, sloc: sloc.physical}`, names class methods `<Class>.<name>` (`<anonymous>` when the class has no name), and sorts by `line`, then `name`.

Also export a `escomplexVersion()` helper (read from `node_modules/typhonjs-escomplex/package.json`) and an `applyEscomplex(files, staged, warnings)` helper. Put them in this module or in a sibling module the entrypoint requires; the wrapper process must stay the only code that loads escomplex itself.

## Files to Change
- `docker/js_complexity/lib/escomplex.js`: new wrapper plus the helpers.
