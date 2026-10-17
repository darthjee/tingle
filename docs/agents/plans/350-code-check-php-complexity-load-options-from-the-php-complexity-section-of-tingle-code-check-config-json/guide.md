# Guide Plan: code_check php_complexity: load options from the php_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- Section `php_complexity` in `~/.tingle/code_check/config.json`. The keys, precedence, errors and the `Config:` header line follow the main plan and spec `docs/agents/specs/code_check/php_complexity/config.md` (§6 has the full example).

## Implementation Steps

### Step 1 — Overview guide
In `docs/guides/code_check.md`:
- Add `php_complexity` to the "reads defaults from the same file" sentence.
- Add a `php_complexity` row to the configuration table, linking `code_check/php_complexity.md#configuration-file`.
- Add a `php_complexity` section to the example JSON.
- Delete the "`php_complexity` does not read this file yet" paragraph.

### Step 2 — php_complexity guide
In `docs/guides/code_check/php_complexity.md`:
- Add a `## Configuration file` section that mirrors `docs/guides/code_check/js_complexity.md`'s: the example (spec §6 without `details`), `### Keys`, `### How the config and the command line combine`, `### Running without the config: --no-config` and `### Config errors`, with the spec's error messages.
- Add `--no-config` to the Options list, "invalid config file" to the exit-status text, and the `Config:` line to the Header description.

## Files to Change
- `docs/guides/code_check.md` — the config table, the example and the removed "not yet" note.
- `docs/guides/code_check/php_complexity.md` — the new Configuration file section and the `--no-config`, exit status and header updates.

## Notes
- Do not document `details`; #351 adds it.
