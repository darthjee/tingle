# Shell Plan: code_check js_complexity: support .vue/.svelte/.astro single-file components

Main plan: [plan.md](plan.md)

## Shared contracts

- Accept `vue`, `svelte` and `astro` in `lib/selection.js`. Everything else
  is in spec `sfc.md`, sections 2–6.
- The `files[]` JSON shape is unchanged. `path` is the original input line,
  and line numbers are the original ones because the line map is the
  identity.
- Extraction errors set `parse_error: true` and leave the file unstaged. They
  add the warning `{"tool": "entrypoint", "path": <line>, "message":
  "unsupported <script lang=\"<lang>\">" | "unterminated frontmatter"}`.
- A no-script component is staged as an all-whitespace module and must end up
  `fta: null`, `parse_error: false`, `duplication: {"lines": 0}`,
  `functions: []`.

## Steps

- [01 — SFC extraction module](shell/01-sfc-extraction.md)
- [02 — Stage SFCs and wire the entrypoint](shell/02-stage-and-wire.md)
- [03 — Fixtures and smoke test](shell/03-fixtures-and-smoke-test.md)
- [04 — Docker Hub description and header comments](shell/04-dockerhub-description.md)

## CI Checks
- `docker/js_complexity`, `scripts/release_image.sh`:
  `scripts/release_image.sh build js_complexity && scripts/release_image.sh smoke-test js_complexity`
  (CircleCI `release` workflow; run it locally because CI only runs it on release).

## Notes
- **Verify the virtual-module names against each tool.** Each tool must treat
  `5.vue.ts` as `.ts` (last extension):
  - FTA: its default extensions plus `/tmp/fta.json`;
  - jscpd: `--formats-exts`;
  - escomplex: `path.extname`.

  If FTA or jscpd keys on a multi-dot suffix instead, fix it in the
  entrypoint's config/flags, never by renaming. The `sfc/<n>.<ext>.<vext>`
  naming is a spec contract.
- **Check the no-script case in practice.** FTA must drop an all-whitespace
  file (`fta: null`), and jscpd/escomplex must give 0 lines and `[]`. If one
  of them instead reports an error or `null` for an empty module, special-case
  it in the entrypoint so it matches the contract.
- **Padding rule:** keep `\r\n`, `\n` and `\r` exactly. Replace every other
  character outside the kept script content with a single space, one per
  UTF-16 code unit or per code point, but consistently. Only line numbers have
  to match; columns do not.
