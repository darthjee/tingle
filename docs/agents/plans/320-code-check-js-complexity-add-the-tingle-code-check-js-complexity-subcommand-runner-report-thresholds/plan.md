# Plan: code_check js_complexity: add the tingle code_check js_complexity subcommand (runner, report, thresholds)

Issue: [320-code-check-js-complexity-...md](../../issues/320-code-check-js-complexity-add-the-tingle-code-check-js-complexity-subcommand-runner-report-thresholds.md)

## Overview
Add `tingle code_check js_complexity <path>` as a new `python/code_check/js_complexity/` package built on `docker_check`, with the same layout as `rubycritic/`. It selects the core JS/TS files on the host, sends them on stdin to the `darthjee/tingle_js_complexity` image (FTA), validates the merged JSON and prints a table and summary ranked by the rounded FTA score, with a `--fail-on` gate. The spec [`subcommand.md`](../../specs/code_check/js_complexity/subcommand.md) (plus [`README.md`](../../specs/code_check/js_complexity/README.md) and [`docker-check.md`](../../specs/code_check/js_complexity/docker-check.md)) is the source of truth for every text, layout and check. This plan does not repeat it.

## Agents involved

- [python](python.md): the package, its registration in `code_check`, completion, and tests.
- [cli](cli.md): `commands/python.json` `short_help`/`long_help`.
- [guide](guide.md): `docs/guides/code_check/js_complexity.md` and the `docs/guides/code_check.md` index.
- [product-owner](product-owner.md): `docs/agents/architecture.md` and the `README.md` command table.

## Shared contracts

These values must be identical in the code, the `long_help` and the docs:

- **Subcommand name:** `js_complexity`, placed after `rubycritic` everywhere (`SUBCOMMAND_NAMES = ("file_size", "rubycritic", "js_complexity")`).
- **One-line description** (`CodeCheck.SUBCOMMANDS`, `long_help` subcommand list, guide index, README): `JavaScript/TypeScript code complexity via FTA (Docker).`
- **`short_help`:** `Code evaluation checks (subcommands: file_size, rubycritic, js_complexity).`
- **Usage:** `tingle code_check js_complexity <path> [options]`. `<path>` is a JavaScript/TypeScript file or directory (recursive).
- **Flags in #320** (help texts from spec §2):
  - `--warn N`, `--error N`, `--critical N`: floats ≥ 0; defaults `50`, `60`, `75`; applied to the file's FTA score;
  - `--top N`: int ≥ 0, default `0` (all);
  - `--min-level ok|warn|error|critical`: default `ok`;
  - `--fail-on warn|error|critical`: no default; exits 2;
  - `--image IMAGE`: default `darthjee/tingle_js_complexity:<tingle version>`.
  
  There is **no** `--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore`, `--include` (#321), `--no-config` or config section (#322), `--details` (#325) and `Dup` column (#324) in this issue. The docs must not mention them as available.
- **Extensions:** `.js .mjs .cjs .jsx .ts .mts .cts .tsx`, case-insensitive. `.d.ts/.d.mts/.d.cts` are always skipped.
- **Default excludes (19):** `node_modules, dist, build, .git, vendor, third_party, .next, __pycache__, .cache, coverage, .nuxt, out, target, .turbo, .svelte-kit, .output, .vercel, .parcel-cache, storybook-static`.
- **No `.gitignore` filtering in #320.** Spec README §6 ships filter steps 1, 5 (extensions), 6 (declaration files) and 7 only. `.gitignore` arrives with #321.
- **Score and levels:** `s = round(fta.score, 1)`. Levels go `critical` ≥ `error` ≥ `warn` ≥ `ok` on `s`. `Cyclo`, `Lines` and `Assessment` are for information only.
- **Exit codes:**
  - `0`: report printed, nothing selected, or `--help`;
  - `1`: a usage error, a path error, a mount root with `:`, an unreadable version file, Docker missing or down, a failed pull, a mount failure, a container failure or unparsable output;
  - `2`: the `--fail-on` gate failed.
- **Messages:** the exact texts in spec §10, e.g. `Error: docker not found on PATH; tingle code_check js_complexity needs Docker to run FTA` and `No JavaScript/TypeScript files found for analysis.`.
- **Report layout:** spec §6 (header with `Analyzing:`, `Thresholds:` and `Image:`; columns `Status FTA Cyclo Lines Assessment File`; summary and `FTA score: avg X | max Y`). The guide reuses the spec's full example output.
