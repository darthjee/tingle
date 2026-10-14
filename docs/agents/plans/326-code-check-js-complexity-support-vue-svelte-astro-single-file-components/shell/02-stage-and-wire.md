# Stage SFCs and wire the entrypoint

- `lib/selection.js`: accept the SFC extensions. Add them to the accepted set
  (or check `EXTENSIONS.has(ext) || SFC_EXTENSIONS.has(ext)`) so they are no
  longer refused as `unsupported extension`.
- `lib/staging.js`: add `SFC_DIR = /tmp/stage/sfc`. For an SFC extension,
  `stageFile` decodes the UTF-8 text (invalid UTF-8 still returns the existing
  "not valid UTF-8" outcome) and calls `extractSfc`.
  - On success, it writes `sfc/<n>.<ext>.<vext>` (with `<ext>` lower-cased)
    and reports success.
  - On an extraction error, it reports the error message so the caller can
    record it. Change the return value from a boolean to a small result such
    as `{ staged: true }`, `{ invalidUtf8: true }` or
    `{ extractionError: msg }`, and update the caller.
  - Update the header comment, which today only describes `plain/`.
- `entrypoint.js` `stageLines`: on an extraction error, set
  `entry.parse_error = true` and push
  `{ tool: "entrypoint", path: line, message }`. Update the header comment:
  accepted extensions, the `sfc/` staging, and the spec reference to
  `sfc.md`.
- `lib/jscpd.js` and `lib/escomplex.js`: no change is expected, because both
  already map `sfc/...` back through `stagedNumber`. Confirm the empty-module
  behaviour (see Notes in [shell.md](../shell.md)), and update any comments
  that still say SFCs are refused.

## Files to Change
- `docker/js_complexity/lib/selection.js` — accept vue/svelte/astro.
- `docker/js_complexity/lib/staging.js` — the `sfc/` staging through
  `extractSfc`, and the richer return value.
- `docker/js_complexity/entrypoint.js` — record extraction errors; update the
  header comment.
- `docker/js_complexity/lib/jscpd.js`, `docker/js_complexity/lib/escomplex.js`
  — comments only, unless the empty-module check needs code.
