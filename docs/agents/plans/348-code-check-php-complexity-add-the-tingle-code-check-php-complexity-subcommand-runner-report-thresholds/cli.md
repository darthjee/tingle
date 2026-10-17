# Cli Plan: code_check php_complexity: add the tingle code_check php_complexity subcommand (runner, report, thresholds)

Main plan: [plan.md](plan.md)

## Shared contracts

Uses the short_help, the Subcommands line, the flags with their help texts, the exit codes and the full example from [plan.md § Shared contracts](plan.md#shared-contracts) and [`cli.md`](../../specs/code_check/php_complexity/cli.md) §1–§2, §9 and §6.

## Implementation Steps

### Step 1 — Update the code_check help
In `commands/python.json`, entry `code_check`, set `short_help` to the shared string. In `long_help`, add the `php_complexity` line under "Subcommands", plus a `php_complexity` part shaped like the `js_complexity` one: usage, file selection (`.php` only, the default excludes, Blade and `bootstrap/cache` skipped), thresholds (total CCN, 20/40/60), display (`--top`, `--min-level`), CI gate (`--fail-on`, exit 2, `PARSE` never gates), image (`--image`), exit codes and examples. Do not document the flags from #349–#352.

## Files to Change
- `commands/python.json` — `code_check` short_help and long_help

## Notes
- Keep the wording consistent with the guide and with the flag help texts in `flags.py`.
