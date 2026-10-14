# Plan: code_check js_complexity: support .vue/.svelte/.astro single-file components

Issue: [326-code-check-js-complexity-support-vue-svelte-astro-single-file-components.md](../../issues/326-code-check-js-complexity-support-vue-svelte-astro-single-file-components.md)

## Overview
The host starts selecting `.vue`, `.svelte` and `.astro` files. The image's
Node entrypoint extracts each component's script blocks into one padded
virtual module under `/tmp/stage/sfc/`, keeping the original line numbers.
FTA, jscpd and escomplex analyse that module like any other staged file, and
the results are written back to the component's own row. Most of the plumbing
already exists: `stagedNumber`, `stagedSizes`, FTA's `Failed to analyze`
regex and the escomplex path listing all accept `sfc/<n>.<ext>.<vext>`
already. Everything ships in one PR, following
`docs/agents/specs/code_check/js_complexity/sfc.md`.

## Agents involved

- [shell](shell.md): SFC extraction and staging in `docker/js_complexity/`,
  the fixtures, the smoke test in `scripts/release_image.sh` and the Docker
  Hub description.
- [python](python.md): `SFC_EXTENSIONS` in the host selection, the help
  docstring and the tests.
- [cli](cli.md): the `long_help` in `commands/python.json`.
- [guide](guide.md): `docs/guides/code_check/js_complexity.md`.
- [product-owner](product-owner.md): `docs/agents/tingle-js-complexity-image.md`
  and `docs/agents/architecture.md`.

## Shared contracts

- **Extensions.** The host sends `.vue`, `.svelte` and `.astro` files (any
  letter case) on stdin, like the core ones. No skip rule applies to them.
  The image accepts `vue`, `svelte` and `astro`, compared on the lower-cased
  last extension, and stops refusing them as `unsupported extension`.
- **JSON shape: unchanged.** An SFC gets the usual `files[]` entry
  (`path`, `parse_error`, `fta`, `duplication`, `functions`), where `path` is
  the original input line (for example `src/Cart.vue`). Python needs no
  SFC-specific parsing.
- **Line numbers** in `functions[].line` and in the duplication ranges are
  the original file's lines. No offset is applied anywhere.
- **No-script component:** `parse_error: false`, `fta: null`,
  `duplication: {"lines": 0}`, `functions: []`. The host already shows it as
  `OK 0.0`.
- **Extraction errors** produce `parse_error: true`, `fta: null` and a
  warning `{"tool": "entrypoint", "path": <line>, "message": <msg>}`, where
  `<msg>` is:
  - `unsupported <script lang="<lang>">`, with `<lang>` as written in the file;
  - `unterminated frontmatter`.

  The host already renders these as `⛔ PARSE` with
  `Warning: cannot parse <file>: <msg>`. Check that the existing parser
  accepts a `PARSE` row whose warning has tool `entrypoint`. If it does not,
  this is the one change the python agent must make.
- **Text** shared by every help or doc mention of the extensions:
  `.vue, .svelte and .astro single-file components (their <script> blocks and
  Astro frontmatter only)`.
