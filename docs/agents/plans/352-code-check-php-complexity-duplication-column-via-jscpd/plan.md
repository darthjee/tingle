# Plan: code_check php_complexity: duplication column via jscpd

Issue: [352-code-check-php-complexity-duplication-column-via-jscpd.md](../../issues/352-code-check-php-complexity-duplication-column-via-jscpd.md)

## Overview
Add jscpd 5.4.1 to the `tingle_php_complexity` image (a build-only Node stage that copies only the native binary), fill `tool_versions.jscpd` and `files[].duplication` in the merged JSON, and show the information-only `Dup` column in `tingle code_check php_complexity`. A jscpd failure is never fatal. The image and Python changes ship in the same PR. Everything follows the normative spec [duplication.md](../../specs/code_check/php_complexity/duplication.md), mirroring `js_complexity` (#324).

## Agents involved

- [shell](shell.md) — `docker/php_complexity/` (Dockerfile, npm pin, entrypoint) and the `smoke_test_php_complexity` assertions in `scripts/release_image.sh`.
- [python](python.md) — `python/code_check/php_complexity/` reporter and executor, plus tests.
- [cli](cli.md) — the `php_complexity` part of `long_help` in `commands/python.json`.
- [guide](guide.md) — `docs/guides/code_check/php_complexity.md`.
- [product-owner](product-owner.md) — `docs/agents/tingle-php-complexity-image.md`.

## Shared contracts

The merged JSON shape is unchanged (already validated by `python/code_check/php_complexity/output_parser.py`); only the values change:

- `tool_versions.jscpd`: `"5.4.1"` (str), read from `/usr/local/bin/jscpd --version` (`^jscpd (\S+)$`). Previously always `null`.
- `files[i].duplication`: `{"lines": int >= 0}` or `null`.
  - `{"lines": n}`: staged, not a parse error, size <= 1,048,576 bytes; `n` = distinct lines of the file covered by any clone range it appears in (`0` when none, including files PDepend reported nothing for, e.g. `bootstrap.php`, `empty.php`).
  - `null`: parse error (PHP or PDepend), refused line, file > 1 MiB, or every file when jscpd failed. Always `null` when `parse_error` is `true`.
- jscpd failure: one warning `{"tool": "jscpd", "message": "<one-line reason>"}` with **no `path`**; reasons exactly as `js_complexity`'s (`jscpd exited with status <s>`, `jscpd killed by <signal>`, `jscpd report /tmp/jscpd/jscpd.json is missing`, `jscpd report /tmp/jscpd/jscpd.json is not valid JSON`, `jscpd report has no duplicates list`, `jscpd report has a malformed duplicates entry`, `jscpd reported an unknown path: <name>`). The entrypoint exit status is unchanged by it.
- An unreadable jscpd version is an entrypoint failure: exit 1, stderr `tingle_php_complexity: cannot read the jscpd version`.
- Tingle stderr for each path-less `jscpd` warning: `Warning: jscpd failed in <image>; duplication data is not available: <message>`. Exit code unchanged.
- Report layout (between `Lines` and `File`):
  - header `f"{'Status':<16} {'CCN':>5}  {'Max':>5}  {'NPath':>7}  {'MI':>5}  {'Lines':>5}  {'Dup':>5}  File"`;
  - separator `─` × 16, 5, 5, 7, 5, 5, 5, 50;
  - level row `duplication.lines` as `{n:>5}`, `-` when `null`; `PARSE` row `-`;
  - summary unchanged; `--details` function lines unchanged.
- Grounding fixture values: `dup_a.php` and `dup_b.php` → `13`; every other analysed fixture file → `0`. Canonical example table: [duplication.md §4](../../specs/code_check/php_complexity/duplication.md#4-report).
