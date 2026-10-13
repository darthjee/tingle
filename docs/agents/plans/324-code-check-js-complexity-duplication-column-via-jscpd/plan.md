# Plan: code_check js_complexity: duplication column via jscpd

Issue: [324-code-check-js-complexity-duplication-column-via-jscpd.md](../../issues/324-code-check-js-complexity-duplication-column-via-jscpd.md)

## Overview
Add jscpd 5.4.1 to the `tingle_js_complexity` image. The entrypoint runs it on the staged tree after FTA, fills `files[].duplication` and `tool_versions.jscpd`, and turns any jscpd failure into one path-less `jscpd` warning. On the Python side, the reporter gets an information-only `Dup` column and the executor prints the jscpd failure warning. The image and the Python changes land in the same PR. `docs/agents/specs/code_check/js_complexity/duplication.md` is authoritative for every exact value.

## Agents involved

- [shell](shell.md)
- [python](python.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

The merged JSON shape is unchanged. Only values that were always `null` now get filled:

- `tool_versions.jscpd`: `"5.4.1"` (str), read from `node_modules/jscpd/package.json`. It is kept even when jscpd fails.
- `files[].duplication`: `{"lines": <int >= 0>}` or `null`.
  - `{"lines": 0}`: staged, read by jscpd, in no clone. This includes a file FTA dropped, such as `empty.js`.
  - `{"lines": n}`: n is the number of distinct line numbers of the file covered by any clone range. The file can be `firstFile` or `secondFile`, and a clone inside one file contributes both ranges.
  - `null`: a staged file over 1,048,576 bytes, `parse_error: true`, a refused line, or every file when jscpd failed.
- Failure warning: `{"tool": "jscpd", "message": "<one-line reason>"}`, **without** `path`. There is at most one per run, and the entrypoint's exit status is unchanged.
- Python stderr for each path-less `jscpd` warning: `Warning: jscpd failed in <image>; duplication data is not available: <message>`.
- Report column: `Dup` (`{:>5}`) between `Lines` and `Assessment`. The header is `f"{'Status':<16} {'FTA':>5}  {'Cyclo':>5}  {'Lines':>5}  {'Dup':>5}  {'Assessment':<17}  File"` and the separator is `─` × 16, 5, 5, 5, 5, 17, 50. A level row shows `duplication.lines`, or `-` when `null`. A `PARSE` row shows `-`. The column is information only: no effect on the level, the gate, the exit code or the summary.
- Fixture grounding: `dup_a.js` and `dup_b.js` each have `duplication.lines == 22` (the smoke test asserts `>= 20`). Every other staged fixture file has `0`.
