# Issue: code_check php_complexity: duplication column via jscpd

## Description
Add an information-only duplication column, `Dup`, to `tingle code_check php_complexity` (parent #344), using [jscpd](https://github.com/kucherenko/jscpd), as `js_complexity` did in #324. `phpcpd` is not used because it was archived in 2023.

**Normative spec:** `docs/agents/specs/code_check/php_complexity/duplication.md` (cross-referenced from `image.md`, `cli.md` and `release.md` in the same folder).

Depends on #347 (release pipeline) and #348 (subcommand core), both merged. #353 (removing the specs folder) comes after this issue.

## Problem
Today the `tingle_php_complexity` image always emits `tool_versions.jscpd: null` and `files[].duplication: null`, and the report has no duplication information. Copy-pasted PHP code goes unnoticed, while `js_complexity` already reports it.

## Expected Behavior
- **Image:** `docker/php_complexity/` gets `package.json`/`package-lock.json` pinning jscpd `5.4.1` (the same version as `docker/js_complexity/`). A build-only Node stage installs it with `npm ci` and copies only the native `jscpd` binary into the final image, so the final image has **no Node** (`command -v node` fails). `.dockerignore` excludes `node_modules/`.
- **Run:** after PDepend, when at least one file is staged, the entrypoint runs jscpd on the staged tree (`/tmp/stage`) with every option that affects the result pinned (`--min-tokens 50 --min-lines 5 --mode mild --kind exact --format php --formats-exts php:php --no-gitignore --max-size 1mb`, JSON report at `/tmp/jscpd/jscpd.json`). jscpd's stdout and stderr go to the entrypoint's stderr.
- **Version:** `tool_versions.jscpd` comes from `jscpd --version` (`jscpd 5.4.1` → `"5.4.1"`). An unreadable version is an entrypoint failure (exit 1, `tingle_php_complexity: cannot read the jscpd version`).
- **Per-file value:** `duplication.lines` is the number of the file's distinct lines covered by any clone range it appears in (each line counted once). `{"lines": 0}` for analysed files with no clone (including files PDepend reported nothing for); `null` for parse errors, refused lines, files over 1 MiB, and every file when jscpd fails.
- **Duplication across the selection only:** jscpd only sees the staged tree, so clones with excluded or ignored files (e.g. `vendor/`) are never counted.
- **Report:** a 5-wide `Dup` column between `Lines` and `File`; `-` when `duplication` is `null` and on `PARSE` rows. It is information only: it never decides the level or the exit status. The summary does not change. With `--details`, the file rows carry the column too; the per-function drill-down lines are unchanged.
- **jscpd failure** (non-zero exit, killed, missing/invalid report, malformed entry, unknown path): every `duplication` is `null`, one `{"tool": "jscpd", "message": ...}` warning without a `path` is added, and the run goes on. Tingle prints `Warning: jscpd failed in <image>; duplication data is not available: <message>` to stderr; the exit code is unchanged.
- **Smoke test:** also asserts `tool_versions.jscpd == "5.4.1"`, `13` for `dup_a.php`/`dup_b.php`, `0` for every other analysed file, `null` for parse errors and refused lines, no `jscpd` warning, and no `node` in the image.

## Solution
- The image change (Dockerfile Node stage, `package.json`, `package-lock.json`, `entrypoint.php`/`lib`, smoke test) and the Python change (output parser, reporter, warning) land **in the same PR**.
- Docs updated in the same PR: `docs/guides/code_check/php_complexity.md` (the `Dup` column), the `long_help` text, `docs/agents/tingle-php-complexity-image.md` (the Node stage, the jscpd pin and its bump procedure: update `package.json`, regenerate `package-lock.json` inside the Node image with `npm install --package-lock-only`, keep it equal to `docker/js_complexity/`'s version), `DOCKERHUB_DESCRIPTION.md` and `DOCKERHUB_SHORT_DESCRIPTION.txt`.
- Python tests cover the column with a number, `0` and `null`; `PARSE` rows; the warning for a `jscpd` entry without a `path`; and the exit code unchanged by it.

## Benefits
- Surfaces copy-pasted PHP code next to the complexity metrics, at parity with `js_complexity`.
- Keeps the published image lean (no Node runtime) and the jscpd version aligned across both images.
