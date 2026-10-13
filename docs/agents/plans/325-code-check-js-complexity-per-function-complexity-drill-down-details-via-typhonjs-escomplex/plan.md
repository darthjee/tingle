# Plan: code_check js_complexity: per-function complexity drill-down (--details) via typhonjs-escomplex

Issue: [325](../../issues/325-code-check-js-complexity-per-function-complexity-drill-down-details-via-typhonjs-escomplex.md)

## Overview
This plan adds typhonjs-escomplex 0.1.0 to the `tingle_js_complexity` image. A separate wrapper process fills `files[].functions` and `tool_versions.escomplex` in the merged JSON. On the Python side it adds `--details [N]` and the `details` config key, which list each shown row's most complex functions under it. Per-function data is information only: it never sets a level or changes the exit code. The image and Python changes land in the same PR. The full contract is in [`docs/agents/specs/code_check/js_complexity/details.md`](../../../../docs/agents/specs/code_check/js_complexity/details.md).

## Agents involved

- [shell](shell.md): image deps, the escomplex wrapper, entrypoint wiring, the smoke test and the Docker Hub description
- [python](python.md): the flag, constant, config key, reporter, warning and tests (help and completion come from `FLAGS`)
- [product-owner](product-owner.md): `docs/agents/tingle-js-complexity-image.md` and the config comment cleanups in the specs, if any
- [guide](guide.md): `docs/guides/code_check/js_complexity.md`

`cli` has no work. `--help` and completion are generated from `code_check.js_complexity.flags.FLAGS` (`python/code_check/completion.py`), so nothing under `bin/` or `commands/` changes.

## Shared contracts

- **Merged JSON** (image stdout, unchanged envelope):
  - `tool_versions.escomplex`: `"0.1.0"` (string; read from `node_modules/typhonjs-escomplex/package.json`). It stays set even when the wrapper fails.
  - `files[i].functions`: `null` or a list of `{"name": str, "line": int>=1, "cyclo": int>=1, "sloc": int>=1}` in source order (by `line`, then `name`). Methods are named `"<Class>.<name>"` (`<anonymous>` for an unnamed class), and anonymous functions are `"<anon method-N>"`. A file with no function gives `[]`. A `parse_error` file, a refused line, or a file escomplex could not parse gives `null`.
  - `warnings[]`: a per-file escomplex failure is `{"tool": "escomplex", "path": <sent line>, "message": <one line>}`. A failure of the whole wrapper is `{"tool": "escomplex", "message": <one line>}` with no `path`, and every `functions` is `null`. The entrypoint exit status never changes because of escomplex.
- **Python side:** `output_parser.py` already validates all of the above (`FileResult.functions`, `WARNING_TOOLS` includes `escomplex`). No parser change is expected.
- **CLI:** `--details [N]` (int, `nargs="?"`, `const=Constants.DEFAULT_DETAILS` = 5, default `None`). Help: `Show the N most complex functions under each file (default when given without N: 5; 0 = all)`. A negative value gives `Error: --details must be an integer >= 0`, exit 1 (already enforced by `docker_check` once `details` is in `SINGLE_DEFAULTS`).
- **Config:** `details` in the `js_complexity` section: `nullable_non_negative_int` (`'details' must be an integer >= 0 or null`). The precedence is built-in `None` < config < CLI.
- **Output:**
  - Function line: `f"{c.DIM}{'':<16} cyclo {f.cyclo:>3}  sloc {f.sloc:>4}  {f.name}  ({path}:{f.line}){c.RESET}"`.
  - Unavailable note: `f"{c.DIM}{'':<16} (per-function data unavailable){c.RESET}"`.
  - Wrapper failure warning (stderr): `Warning: escomplex failed in <image>; per-function data is not available: <message>`.
