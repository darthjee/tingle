# Product-owner Plan: code_check php_complexity: load options from the php_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- `config.py` holds the real `php_complexity` schema (12 keys, no `details` yet), and `flags.py` gains `--no-config`.

## Implementation Steps

### Step 1 — Architecture doc
In `docs/agents/architecture.md` (around line 321), replace "a stub that accepts nothing until #350" with a description of the real schema (`js_complexity`'s keys minus `details`, which #351 adds). Update the `flags.py` bullet so it lists the selection flags and `--no-config` as present, with `--details` still to come from #351.

## Files to Change
- `docs/agents/architecture.md` — the `php_complexity` `config.py` and `flags.py` bullets.

## Notes
- The temporary specs under `docs/agents/specs/code_check/php_complexity/` stay; the epic's last sub-issue removes them.
