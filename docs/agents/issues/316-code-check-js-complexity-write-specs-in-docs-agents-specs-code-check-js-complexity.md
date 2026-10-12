# Issue: code_check js_complexity: write specs in docs/agents/specs/code_check/js_complexity/

## Description
Write the specs for the new `tingle code_check js_complexity <path>` subcommand (parent #315). The subcommand measures JavaScript/TypeScript code complexity by running [FTA](https://ftaproject.dev/) inside a published Docker image, `darthjee/tingle_js_complexity`. [jscpd](https://github.com/kucherenko/jscpd) adds duplication data and [typhonjs-escomplex](https://github.com/typhonjs-node-escomplex/typhonjs-escomplex) adds per-function data. This mirrors `tingle code_check rubycritic` (#290).

The specs go under `docs/agents/specs/code_check/js_complexity/`, and `docs/agents/specs.md` indexes them. They are temporary: #327, the last sub-issue of #315, removes them once everything has landed.

## Problem
#315 is split into this specs sub-issue (#316), ten implementation sub-issues (#317–#326) and a cleanup (#327):
- the `docker_check` refactor (#317)
- the image (#318) and its release pipeline (#319)
- the core (#320), selection (#321), config (#322), minified-skip (#323), duplication (#324), `--details` (#325) and SFC (#326) sub-issues

Several of them share contracts:
- the CLI and flag names
- the config keys
- the image stdin/stdout contract and the merged JSON shape
- the FTA/jscpd/escomplex fields used
- the `docker_check` module boundary
- exit codes

Without one agreed, normative source, the parallel image track and Python track would drift apart. Also, the tool output shapes that #315's design relies on (FTA's per-file JSON, jscpd's clone report, escomplex's per-function data) have not been checked against real output.

## Expected Behavior
### What the specs must pin down
Add a shared `README.md` for the contracts used by more than one sub-issue, plus one spec per concern:
- **CLI:** `tingle code_check js_complexity <path>`.
  - `--warn/--error/--critical`: numbers ≥ 0, defaults `50/60/75`, applied to FTA's per-file `fta_score`.
  - Display flags: `--top`, `--min-level`.
  - `--fail-on`: exits 2.
  - `--image`.
  - Selection flags: `--exclude`/`--no-default-excludes`, `--ignore`, `--include`, `--no-gitignore`.
  - `--no-config`.
  - `--details [N]`: `5` when given alone, `0` means all.
  - There is no `--ext`.
- **Extensions:**
  - Core: `.js .mjs .cjs .jsx .ts .mts .cts .tsx`, matched regardless of case.
  - Always skipped: `.d.ts/.d.mts/.d.cts`.
  - Skipped by default: minified `*.min.js/.mjs/.cjs`.
  - Added by #326 (SFC): `.vue .svelte .astro`.
- **Report:** the same layout as `file_size`/`rubycritic`.
  - Columns: `Status`, `FTA`, `Cyclo`, `Lines`, `Dup` (jscpd duplicated lines; information only), `Assessment` (FTA's label; information only), `File`.
  - Rows are sorted by `fta_score`, highest first.
  - Summary: file counts per level, plus `FTA score: avg X | max Y`.
  - `⛔ PARSE` rows for files FTA can't parse. They count as skipped and never trigger `--fail-on`.
- **Image contract:**
  - The same `docker run --rm -i --network none --user <uid>:<gid> -v <path>:/src:ro -w /src <image>` as rubycritic, with the file list on stdin, one path per line.
  - The entrypoint merges the FTA, jscpd and escomplex results into **one JSON document on stdout**, with a fixed shape (see the merged JSON contract under [Decided choices](#decided-choices)).
  - Everything else goes to stderr; an FTA failure means a non-zero exit.
  - A jscpd or escomplex failure is reported in the JSON's `warnings` instead of failing the run.
- **Tool input (staged tree):** FTA walks a directory and does not take a file list, so the entrypoint stages the input. The details are under [Decided choices](#decided-choices).
- **`docker_check` boundary:** what moves from `python/code_check/rubycritic/` into `python/code_check/docker_check/` (runner, image resolution, selection, executor scaffolding), what stays per check, and the parameters (image repository, extensions, extra skip rules, error class).
- **Default image:** `darthjee/tingle_js_complexity:<tingle version>`.
- **Config:** the `js_complexity` section.
  - Keys: `warn`, `error`, `critical`, `top`, `exclude`, `no_default_excludes`, `ignore`, `include`, `gitignore`, `fail_on`, `min_level`, `image`, and `details` (added by #325).
  - No `ext`.
  - The rules are the same as `rubycritic`.
- **Default excludes:** `file_size`'s `DEFAULT_EXCLUDES` plus `.turbo`, `.svelte-kit`, `.output`, `.vercel`, `.parcel-cache`, `storybook-static`.
- **Exit codes:** 0 when all is well; 1 for Docker problems, an FTA failure, unparsable output, a bad path or a config error; 2 only for `--fail-on`.
- **Edge cases:** every case in #315's "Edge cases" section. That includes:
  - escomplex failing where FTA succeeds: `(per-function data unavailable)`;
  - a secondary tool failing: degrade with a warning;
  - SFCs with no script, several script blocks, `src=` scripts, or an unknown `lang`;
  - duplication counted only within the selection.

### Decided choices
These were decided while refining #316. The specs record them as normative rules, unless the grounding run contradicts them; in that case the spec says so explicitly and proposes the closest alternative.

- **Tool input: a staged tree under `/tmp`** (`image.md`).
  - The entrypoint symlinks or copies each stdin path into `/tmp/stage/<same relative path>`. The grounding run decides between symlink and copy, depending on whether FTA follows symlinks.
  - It runs **every tool** (FTA, and later jscpd and escomplex) on that staged tree, never on `/src` directly. That way each tool sees exactly the selected files.
  - Paths in the merged JSON are mapped back by stripping the `/tmp/stage/` prefix, so they come out relative to the mount root, the same as the stdin lines.
  - The same tree holds the extracted SFC scripts for #326.
  - Nothing is written outside `/tmp`.
- **SFC files with several script blocks: combined into one unit** (`sfc.md`, #326).
  - All script blocks of a `.vue`/`.svelte`/`.astro` file are joined in file order into one virtual module, staged as `<path>.<ext>.ts` or `.js`. It is TS if **any** block is TS. It is analysed once, so the file gets one FTA score, one cyclo, one set of duplication ranges and one set of functions.
  - Per-block results are not summed, because FTA and Halstead scores are not additive.
  - A line map from virtual-module lines back to the original file's lines is kept. It is used for the `--details` line numbers and for jscpd ranges.
- **Minified files and `--include`** (`file-selection.md`, #323). The minified skip (`*.min.js/.mjs/.cjs`) is a **default exclude**.
  - `--include` only ever narrows the selection, so it never brings minified files back.
  - Only `--no-default-excludes`, or `"no_default_excludes": true`, turns the skip off.
  - A single-file `<path>` that is minified follows the same rule.
- **Merged JSON contract: a fixed shape, with `null` for parts not yet available** (`README.md` summary, full definition in `image.md`).
  - #316 pins the **complete** shape from day one. #318 already emits every key, with `duplication: null` and `functions: null` per file, and `jscpd`/`escomplex: null` in `tool_versions`. #324 and #325 only fill in their parts; they never add or rename keys.
  - There is **no `version` field and no version negotiation**: the image and the CLI are always released under the same tingle tag. A key that is missing, or of the wrong type, is an unparsable-output error (exit 1).
  - **One entry per stdin line, in stdin order**, even for files a tool dropped or failed on, so the parser never has to diff the selection against the output.
  - `null` means *not available*, and `[]` or `0` means *available and empty*. The report must tell them apart: `Dup` shows `-` for `null` and `0` for 0; `--details` shows `(per-function data unavailable)` for `null` and nothing for `[]`.
  - The spec defines the exact field rules, the per-file states (normal, parse error, dropped), and the `warnings` entries (`tool`, `message`, optional `path`). The final field names may be adjusted to fit the real tool output from the grounding run, but the shape rules above are fixed.

  Sketch:

  ```json
  {
    "tool_versions": {"fta": "x.y.z", "jscpd": null, "escomplex": null},
    "files": [
      {
        "path": "src/app/store.ts",
        "parse_error": false,
        "fta": {"score": 82.4, "cyclo": 61, "lines": 912, "assessment": "Needs improvement"},
        "duplication": null,
        "functions": null
      },
      {"path": "src/broken.js", "parse_error": true, "fta": null, "duplication": null, "functions": null},
      {"path": "src/empty.js", "parse_error": false, "fta": null, "duplication": null, "functions": null}
    ],
    "warnings": []
  }
  ```

  The per-file states are:

  | `parse_error` | `fta` | Report |
  |---|---|---|
  | `false` | object | normal row |
  | `true` | `null` | `⛔ PARSE` row |
  | `false` | `null` | dropped by FTA → `OK`, score 0 |

  After #324 and #325, the parts are filled in: `"duplication": {"lines": 88}` and `"functions": [{"name": "reducer", "line": 120, "cyclo": 18, "sloc": 40}]`.
- **Node base image** (`image.md`, #318). The current **active LTS** line at the time of writing, as `node:<major>.<minor>.<patch>-slim`, pinned to an exact patch, the same way rubycritic pins `ruby:3.3.N-slim`.
  - It is Debian slim (glibc), not Alpine, because FTA ships a native binary.
  - `image.md` records the exact tag; bumping it is a deliberate change.

### Grounding in real tool output
Before writing the image and subcommand specs, the spec author must ground them in real output, the same way #292 did for rubycritic.

**Where it runs.** The run is throwaway: a scratch directory and a throwaway container, with **nothing committed** besides the specs. #316 stays docs-only. `image.md` lists the fixture files that #318 must create under `docker/js_complexity/fixture/`, with the expected result for each file, so the image smoke test checks exactly the cases the specs were grounded on.

1. **Run the tools.** Run the pinned FTA (`fta-cli`), jscpd and typhonjs-escomplex, at the versions to pin, in the target Node slim image **without git**, under `--network none`, with `/src` mounted read-only and a foreign `--user`. Use this fixture:
   - a simple `.js` file and a complex `.ts` file;
   - a `.tsx`/`.jsx` file;
   - two files sharing a duplicated block;
   - a file with a syntax error;
   - an empty file;
   - a `.min.js` file;
   - a `.vue` file with `<script setup lang="ts">`;
   - a CRLF file, a file with a UTF-8 BOM, and a file with non-UTF-8 bytes (see [Additional edge cases](#additional-edge-cases)).
2. **Record in the specs:**
   - for each tool, the **exact command line and the exact versions** used (Node base image tag, `fta-cli`, `jscpd`, `typhonjs-escomplex`), so the run can be repeated when versions are bumped;
   - the exact JSON path of every field the report uses: FTA's `fta_score`, `cyclo`, `line_count` and `assessment`; jscpd's per-file clone ranges; escomplex's per-function name, line, cyclomatic and sloc;
   - how paths appear in each tool's output;
   - a **per-fixture results table**: for each file, its FTA score and assessment, whether it is a parse error, whether it was dropped or missing, its jscpd duplicated lines, and whether escomplex returned functions. This drives the `PARSE`, "OK with score 0" and `(per-function data unavailable)` rules;
   - FTA's actual assessment bands, to confirm the `50/60/75` defaults;
   - whether a read-only `/src`, a foreign uid and no network work, with all temporary output under `/tmp`. Note any tool that tries to reach the network or write outside `/tmp`.
3. **Samples:** put a **trimmed** JSON sample from each tool in the specs as the contract example. Keep one or two entries, with every field the report uses; leave out verbose blocks that tingle ignores, such as most of FTA's Halstead block and jscpd's statistics. Do not paste full raw output.

If real output contradicts a decision in #315, the spec says so explicitly and proposes the closest alternative. It never silently drops a column or rule.

### Additional edge cases
On top of every edge case in #315, the specs must cover these cases, which come from the choices made while refining #316:
1. **Hostile or malformed stdin lines** (`image.md`). The entrypoint never stages anything outside `/src`. It skips each of these lines and adds one entry to `warnings` (`tool: "entrypoint"`, the line, the reason):
   - absolute paths;
   - paths with a `..` segment;
   - empty lines;
   - duplicate lines;
   - paths that don't exist under `/src`.

   Skipped lines still get a `files` entry, so "one entry per stdin line" holds. The spec defines that entry's state, e.g. `parse_error: false, fta: null` plus the warning. Tingle's host-side selection never sends such lines; this is defence in depth.
2. **Staging name collisions** (`image.md`, `sfc.md`). Virtual SFC modules are staged in their own subtree (e.g. `/tmp/stage-sfc/<path>.<ext>.ts`), **separate** from `/tmp/stage/`. That way a real `Cart.vue.ts` and the virtual module for `Cart.vue` can never collide. Both trees map back to the original stdin path.
3. **Encoding and line endings** (`image.md`, `sfc.md`, `details.md`):
   - Files with CRLF line endings, a UTF-8 BOM or non-UTF-8 bytes are part of the grounding run. The spec records what each tool does with them, e.g. whether non-UTF-8 is a parse error.
   - The SFC line map and the `--details` line numbers must stay correct with CRLF and with a BOM.
   - Line counts follow FTA's `line_count` as reported. Tingle never recounts.
4. **Pinned tool tuning** (`image.md`, `duplication.md`, `details.md`). Every option that affects results is pinned explicitly in the entrypoint and recorded in the spec, never left to a tool's built-in defaults. That covers:
   - jscpd's `min-tokens`, `min-lines` and formats/modes;
   - escomplex's parser options (TypeScript, JSX, decorators and other plugins);
   - any FTA options.

   Changing any of them is a deliberate change, the same as a version bump.

### Backward compatibility
The specs must state these invariants explicitly, as normative rules for the sub-issue named in each item:
- **rubycritic is unchanged by the refactor** (`docker-check.md`, #317):
  - for every input, `tingle code_check rubycritic` produces **byte-for-byte identical** stdout, stderr, exit codes, `--help`, tab completion and config validation;
  - the existing tests under `python/tests/code_check/rubycritic/` keep passing, and **only import-path edits are allowed**: no assertion changes and no deleted tests. New `docker_check` tests are added next to them;
  - error class names, message wording and the `rubycritic` config section stay as they are. A shared message wording that would change rubycritic's output is not allowed.
- **The rubycritic image is untouched** (`docker-check.md`): `darthjee/tingle_rubycritic`, `docker/rubycritic/` and its stdin/stdout contract don't change. #317 is Python-only.
- **`file_size` is untouched** (`docker-check.md`): `FileCollector`, `code_check.excludes` and `file_size`'s behaviour stay as they are. `docker_check` only wraps them, and any new parameter is optional with today's behaviour as its default.
- **The release script stays compatible** (`release.md`, #319): calling `scripts/release_image.sh` with no selector still means `linux`, and the `linux` and `rubycritic` selectors behave exactly as before. `js_complexity` is only added.
- **Existing config files keep working** (`config.md`, #322): an existing `~/.tingle/code_check/config.json` with `file_size`/`rubycritic` sections stays valid and means the same. A file without a `js_complexity` section uses the built-in defaults. The new section never makes an existing file invalid.

### Messages
Use the same style as `rubycritic`: `Error: <message>` on stderr then exit 1, and `Warning: <message>` for non-fatal cases. The subcommand spec lists the exact text, reusing rubycritic's Docker messages through `docker_check` and adding the secondary-tool-failure warnings.

## Solution
### Spec file layout
`docs/agents/specs/code_check/js_complexity/`:

| File | Sub-issue | Content |
|---|---|---|
| `README.md` | #315 (parent), #316 | Overview, links to #315 and every sub-issue, the sub-issue map and merge order below (including "#319 lands before the tingle tag that ships #320"), and the shared contracts: CLI/flags, exit codes, config keys, extensions, filter order, merged JSON summary |
| `docker-check.md` | #317 | The `docker_check` module boundary and parameters; rubycritic must not change behaviour |
| `image.md` | #318 | Dockerfile (Node LTS slim, no git), pinned `package-lock.json`, entrypoint contract, staged-tree input, merged JSON v1, smoke-test fixtures, local `:dev` build |
| `release.md` | #319 | `release_image.sh` `js_complexity` selector, CircleCI jobs, amd64/arm64, Docker Hub descriptions, ordering rule |
| `subcommand.md` | #320 | Preflight, JSON parsing and path mapping, report, thresholds, flags, PARSE rows, exit codes, edge cases |
| `file-selection.md` | #321, #323 | Extensions, default excludes, flags, `.gitignore`, symlinks, filter order, minified skip |
| `config.md` | #322 | The `js_complexity` schema, precedence, `--no-config` |
| `duplication.md` | #324 | jscpd invocation, per-file duplicated-lines computation, `Dup` column, failure handling |
| `details.md` | #325 | escomplex wrapper, `--details [N]`, `details` key, unavailable-data note, failure handling |
| `sfc.md` | #326 | Script extraction for `.vue/.svelte/.astro`, `lang` handling, combining blocks into one virtual module, line map |

#316 (specs) and #327 (cleanup) have no feature file. Each feature spec links its own sub-issue at the top and can be read on its own.

### Sub-issue map
`README.md` carries this table: each sub-issue, its spec file, and what it depends on.

| Sub-issue | What | Spec | Depends on |
|---|---|---|---|
| #316 | Specs (this issue) | — | — |
| #317 | Extract `python/code_check/docker_check/` from rubycritic | `docker-check.md` | #316 |
| #318 | Image `docker/js_complexity/`, FTA only | `image.md` | #316 |
| #319 | Release pipeline for `darthjee/tingle_js_complexity` | `release.md` | #318 |
| #320 | Subcommand core | `subcommand.md` | #317 (local image from #318) |
| #321 | File selection flags | `file-selection.md` | #320 |
| #322 | Config section `js_complexity` | `config.md` | #321 |
| #323 | Skip minified bundles | `file-selection.md` | #321 |
| #324 | Duplication via jscpd | `duplication.md` | #319, #320 |
| #325 | `--details` via typhonjs-escomplex | `details.md` | #319, #322 |
| #326 | `.vue/.svelte/.astro` support | `sfc.md` | #324, #325 |
| #327 | Cleanup: remove the specs | — | #316–#326 |

**Merge order**
- After #316, three tracks run in parallel: #317, #318 → #319, and #320 → #321 → #322 (after #317).
- #319 must be merged before the tingle tag that ships #320 is pushed.
- #324, #325 and #326 each change the image and the Python side in the same PR.

### Specs index
In `docs/agents/specs.md`, replace "None currently." under **Current specs** with:

| Topic | Specs | Parent issue | Sub-issues |
|---|---|---|---|
| `code_check js_complexity` | [code_check/js_complexity/](specs/code_check/js_complexity/README.md) | #315 | #316 #317 #318 #319 #320 #321 #322 #323 #324 #325 #326 #327 |

#327 removes this row and restores "None currently." if no other specs remain.

### Scope
**In scope**
- New files under `docs/agents/specs/code_check/js_complexity/`: `README.md`, `docker-check.md`, `image.md`, `release.md`, `subcommand.md`, `file-selection.md`, `config.md`, `duplication.md`, `details.md` and `sfc.md`.
- The `code_check js_complexity` row in `docs/agents/specs.md`, replacing "None currently.".
- The throwaway grounding run, recorded in the specs only.
- A **"Deviations from #315"** section in `README.md`. It lists every decision the specs change compared with #315's body or the sibling issue bodies, whether because of the grounding run or the choices made while refining #316, with the affected sub-issue and spec section. If nothing changed, it says "None".

**Out of scope**
- Any implementation: no Dockerfile, entrypoint, CI, Python, Makefile or fixture files. The fixture used for the grounding run is not committed; #318 creates `docker/js_complexity/fixture/` from the list in `image.md`.
- Any other file besides the two above. `docs/agents/folder-structure.md`, `architecture.md`, `.claude/agents/*.md`, `docs/agents/todo.md`, the guides and the `README.md` table are updated by the implementing sub-issues.
- Editing or commenting on the sibling issues #317–#327 on GitHub. **The specs are normative and take precedence over the issue bodies.** Implementers read their spec file and the "Deviations from #315" section.

### Verification
This is a docs-only change, so it is checked by review, plus these mechanical checks:
- every relative link in the new specs and in the `specs.md` row resolves;
- every feature spec links its sub-issue at the top, and `README.md` links #315 and #316–#327;
- the `README.md` sub-issue map matches the table in this issue, and "Deviations from #315" is present (or says "None");
- every rule is normative ("must"/"is"), as `docs/agents/specs.md` requires;
- `git diff --stat` shows only `docs/agents/specs/code_check/js_complexity/**` and `docs/agents/specs.md`.

### Agents
- `product-owner` writes the specs and runs the tool checks using Docker.

## Benefits
- A single normative contract lets the refactor, image and Python tracks proceed in parallel.
- The report design is based on real tool output rather than assumptions.
