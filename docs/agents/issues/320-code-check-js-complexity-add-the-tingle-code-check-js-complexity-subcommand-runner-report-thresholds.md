# Issue: code_check js_complexity: add the tingle code_check js_complexity subcommand (runner, report, thresholds)

## Description
Add the `tingle code_check js_complexity <path>` subcommand (parent #315). It selects the JS/TS files on the host, runs the `darthjee/tingle_js_complexity` image through the shared `python/code_check/docker_check/` package, and prints a `file_size`/`rubycritic`-style report driven by FTA's per-file score.

Spec: `docs/agents/specs/code_check/js_complexity/subcommand.md` (and the `README.md` contracts). The spec is the source of truth for exact texts, layouts and checks.

## Problem
Tingle can measure Ruby complexity (`rubycritic`) but not JavaScript or TypeScript.

## Expected Behavior
- **Package:** `python/code_check/js_complexity/` (`flags`, `constants`, `errors`, `selection`, `output_parser`, `reporter`, `executor`), with `CheckJsComplexity(DockerCheck)`. It reuses `docker_check` for the preflight, pull, runner, image resolution, selection and the `--fail-on` gate. No config section is loaded yet (that is #322).
- **Selection** (core only):
  - `.js .mjs .cjs .jsx .ts .mts .cts .tsx`, matched regardless of case;
  - `.d.ts/.d.mts/.d.cts` are always skipped;
  - the default excludes are `file_size`'s plus `.turbo`, `.svelte-kit`, `.output`, `.vercel`, `.parcel-cache`, `storybook-static`;
  - symlinks pointing outside the mount root, or dangling, are skipped silently;
  - file names containing a newline, or not valid UTF-8, are skipped with a warning;
  - no binary check: a non-UTF-8 file reaches the image and becomes a `PARSE` row.
- **Parsing:** the whole merged JSON shape is validated from the start (including `duplication`, `functions` and the `jscpd`/`escomplex` versions, which are not displayed yet), and `files[i]` is mapped back to sent line `i`. The score `s` is `round(fta.score, 1)` and drives the level, sort, gate, display and summary.
- **Report:**
  - header: `Analyzing:`, `Thresholds: warn=50 | error=60 | critical=75`, `Image: <image>`;
  - a table with the columns `Status`, `FTA` (1 decimal), `Cyclo`, `Lines`, `Assessment` (information only), `File`, sorted by `s` (highest first, ties by sent line);
  - `⛔ PARSE` rows below the level rows, always shown, counted as skipped, with a `Warning: cannot parse ...` on stderr;
  - the summary: file counts per level (plus `skipped (parse error)` when any), then `FTA score: avg X | max Y` over the level rows (`PARSE` rows excluded; `n/a` when there are none).
- **Flags:**
  - `--warn/--error/--critical`: numbers ≥ 0, decimals allowed, not checked against each other;
  - `--top N` and `--min-level`: display only;
  - `--fail-on <level>`: exits 2, over every selected file, never because of `PARSE` rows;
  - `--image`: the default is `darthjee/tingle_js_complexity:<tingle version>`;
  - usage errors exit 1 (argparse's 2 is remapped).
- **Edge cases:**
  - files FTA drops (no code lines) and lines the image refuses are reported as `OK` with a score of 0.0;
  - a single-file `<path>` mounts its parent directory;
  - a missing or unreadable path, a mount root with `:`, an unreadable tingle version without `--image`, Docker missing or down, a failed pull, a non-zero container status or unparsable output exit 1;
  - nothing selected gives the header, `No JavaScript/TypeScript files found for analysis.` and exit 0, with no Docker call;
  - the Docker Desktop file-sharing hint on a mount failure.
- **Exit codes:** 0 OK, 1 error, 2 for `--fail-on` only.
- **Registration:** `"js_complexity"` in `SUBCOMMAND_NAMES` (`python/code_check/subcommands.py`) and `CodeCheck.SUBCOMMANDS` (after `rubycritic`), `commands/python.json` `short_help`/`long_help`, and tab completion from `js_complexity.flags.FLAGS`.
- **Docs:** the new guide `docs/guides/code_check/js_complexity.md` (with the Podman note and the `--ignore`/`--exclude` advice for generated code and unnamed minified bundles), the `docs/guides/code_check.md` index, `docs/agents/architecture.md` and the `README.md` table.
- **Tests:** Python unit tests under `python/tests/code_check/js_complexity/` with `shutil.which` and `subprocess.run` mocked, using sample merged JSON taken from the spec; coverage stays at or above 75%.

## Solution
Mirror `python/code_check/rubycritic/`'s structure on top of `docker_check`. Use a local `tingle_js_complexity:dev` build (`make js-complexity-image`) through `--image` for manual end-to-end checks.

The prerequisites are merged: the `docker_check` refactor (#317), the image (#318) and the release pipeline (#319).

### Out of scope
These have their own sub-issues:
- `--exclude`/`--ignore`/`--include`/`--no-gitignore`/`--no-default-excludes` (#321)
- the config section (#322)
- the minified skip (#323)
- the `Dup` column (#324)
- `--details` (#325)
- `.vue/.svelte/.astro` files (#326)

### Agents
- `python`: the package and tests.
- `cli`: `commands/python.json` help and completion.
- `guide`: `docs/guides/code_check/js_complexity.md` and the index.
- `product-owner`: `architecture.md` and the README table.

## Benefits
- JS/TS complexity can be measured without Node on the host, with the same report and CI gate as the other checks.
