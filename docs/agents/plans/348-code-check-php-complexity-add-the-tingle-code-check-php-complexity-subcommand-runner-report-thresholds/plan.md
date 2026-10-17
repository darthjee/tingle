# Plan: code_check php_complexity: add the tingle code_check php_complexity subcommand (runner, report, thresholds)

Issue: [348](../../issues/348-code-check-php-complexity-add-the-tingle-code-check-php-complexity-subcommand-runner-report-thresholds.md)

## Overview
Add `tingle code_check php_complexity <path>`: a new `python/code_check/php_complexity/` package that mirrors `js_complexity/` (#320) on top of the unchanged `docker_check` package. It selects `.php` files on the host, runs them through the PDepend image, and prints a CCN-ranked report with thresholds and a `--fail-on` gate. The help, the user guide and the agent docs and README ship in the same PR. The normative contract is [`cli.md`](../../specs/code_check/php_complexity/cli.md) plus [`README.md`](../../specs/code_check/php_complexity/README.md). If this plan and the spec disagree, the spec wins.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Subcommand name:** `php_complexity`. The `SUBCOMMANDS` entry, placed after `js_complexity`, is `"php_complexity": (CheckPhpComplexity, "PHP code complexity via PDepend (Docker).")`. `SUBCOMMAND_NAMES = ("file_size", "rubycritic", "js_complexity", "php_complexity")`.
- **short_help** (`commands/python.json`, `code_check`): `Code evaluation checks (subcommands: file_size, rubycritic, js_complexity, php_complexity).`
- **long_help Subcommands line:** `php_complexity   PHP code complexity via PDepend (Docker).`
- **Flags added here** (cli.md §2): `--warn N` (20), `--error N` (40), `--critical N` (60), all numbers ≥ 0 with decimals allowed; `--top N` (int ≥ 0, default 0 = all); `--min-level ok|warn|error|critical` (default `ok`); `--fail-on warn|error|critical` (no default); `--image IMAGE` (default `darthjee/tingle_php_complexity:<tingle version>`). Help texts are exactly the ones in cli.md §2.
- **Level metric:** the total CCN per file. `Max`, `NPath`, `MI` and `Lines` are shown for information only.
- **Report columns:** `Status  CCN  Max  NPath  MI  Lines  File`, sorted by CCN, highest first. `⛔ PARSE` rows come last and are counted as `skipped (parse error)`. They never trigger `--fail-on`. The summary line is `CCN: avg X | max Y`, or `CCN: n/a` when there is no level row.
- **Selection in #348:** `.php` in any case, minus the default excludes (`file_size`'s list plus `var`, `storage`, `.phpunit.cache`), minus `*.blade.php`, minus the `bootstrap/cache` rule. No selection flags yet (#349). When nothing is selected, the output is `No PHP files found for analysis.` and the exit code is 0.
- **Exit codes:** `0` OK, `1` error, `2` the `--fail-on` gate (cli.md §9). Messages are in cli.md §10.
- **Full example output:** cli.md §6 "Full example" (the grounding fixture run). The help and the guide must quote it, or stay consistent with it.
