# Issue: code_check js_complexity: per-function complexity drill-down (--details) via typhonjs-escomplex

## Description
Add a per-function drill-down, `--details [N]`, to `tingle code_check js_complexity` (parent #315). It runs [typhonjs-escomplex](https://github.com/typhonjs-node-escomplex/typhonjs-escomplex) in the `darthjee/tingle_js_complexity` image and works like `rubycritic --details` (#291).

Spec: `docs/agents/specs/code_check/js_complexity/details.md`.

## Problem
FTA scores whole files. A CRITICAL file doesn't tell you which functions to refactor first.

## Expected Behavior
- **Image** (`docker/js_complexity/`):
  - `typhonjs-escomplex` `0.1.0` is pinned exactly in `package.json`, with its whole tree locked in `package-lock.json`.
  - `tool_versions.escomplex` is read from `node_modules/typhonjs-escomplex/package.json`.
  - A wrapper, `lib/escomplex.js`, runs as a **separate process** after FTA and jscpd. It reads the staged file list as a JSON array on stdin and writes a JSON object on stdout that maps each path to `{"functions": [...]}` or `{"error": ...}`.
  - Module options are pinned, and parser plugins are chosen by the staged file's last extension. This avoids the `jsx`+`typescript` clash on `<T>value`.
  - Each function becomes `{name, line, cyclo, sloc}`. Methods come out as `Class.method`, and the list is flattened and kept in source order.
  - A per-file parse failure gives `functions: null` plus a `warnings` entry with a `path`. A wrapper crash gives `null` for every file plus one `warnings` entry without a `path`. Neither changes the entrypoint's exit status.
  - The smoke test and the Docker Hub description are updated.
- **Subcommand:**
  - `--details [N]` lists the `N` most complex functions under each shown level row, sorted by cyclo descending, then line, then name. It applies after `--min-level` and `--top` and never shows under a `PARSE` row. `--details` alone means `5`, `0` means all, and a negative value is an error with exit 1. `DEFAULT_DETAILS = 5` lives in `constants.py`.
  - A `null` value shows one dim line, `(per-function data unavailable)`, and `[]` shows nothing. The row keeps its FTA level and the exit code doesn't change.
  - Each `escomplex` warning without a `path` prints one `Warning: escomplex failed in <image>; per-function data is not available: <message>` line to stderr, with the exit code unchanged. Per-file warnings are not printed.
  - Config key `details`: `nullable_non_negative_int` in the `js_complexity` section, with the precedence built-in `null` < config < CLI.
- `--help`/`long_help`, completion (a free-form value), the guide, `docs/agents/tingle-js-complexity-image.md` and the Python tests are updated, as listed in spec §8.

## Solution
Follow the spec. Mirror #291's reporter logic and reuse it through `docker_check` where that fits. `output_parser.py` already accepts `files[].functions` and `tool_versions.escomplex`, so the Python side is the flag, config, reporter and warning output. Change the image and the Python side **in the same PR**. The image tag follows `shell/linux/VERSION`, so no image-tag change is needed.

Dependencies: the release pipeline (#319), config (#322) and jscpd (#324) are all merged. SFC support (#326) is still open. The wrapper picks plugins by the staged file's last extension, so SFC virtual modules (`….vue.ts`) work once #326 stages them, and #325 doesn't depend on #326.

### Agents
- `shell`: the image, the wrapper, the entrypoint wiring and the smoke test.
- `python`: the flag, config, reporter, warnings and tests.
- `cli`: help and completion.
- `guide`: `docs/guides/code_check/js_complexity.md`.
- `product-owner`: `docs/agents/tingle-js-complexity-image.md`.

## Benefits
- The report points at the exact functions to refactor.
- Per-function data is information only, so it can't break the run or change the gate.
