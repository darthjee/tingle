# Guide Plan: code_check rubycritic: load options from the rubycritic section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

The `python` agent adds `--no-config` and the `rubycritic` config section; see [plan.md](plan.md#shared-contracts) for the keys, defaults, precedence, the `Config: <path>` header line and the `Error: <path>: <reason>` exit-1 errors.

## Implementation Steps

### Step 1 — code_check.md
In `docs/guides/code_check.md` → "Configuration file":

- Add a `rubycritic` row to the table: section `rubycritic`, linking to `code_check/rubycritic.md#configuration-file`.
- Remove the "`rubycritic` does not read the config file yet" note.
- Extend the JSON example with a small `rubycritic` section, if the example is meant to show several sections.

### Step 2 — code_check/rubycritic.md
In `docs/guides/code_check/rubycritic.md`:

- **New "Configuration file" section**, mirroring `code_check/file_size.md#configuration-file`:
  - The location and the section name.
  - A key table with types and defaults, noting that there is no `ext`.
  - The precedence rules, with list merging and deduplication.
  - `--no-config`.
  - What happens with a missing file, a missing section or an empty section.
  - An example config, and a command showing which values win (see [config.md §6](../../specs/code_check/rubycritic/config.md#6-example)).
- **Options:** add `--no-config`.
- **Header:** mention the `Config:` line.
- **"Exit status and errors":** add the config error messages.
- **"Limitations":** remove the "No configuration file yet" bullet.

## Files to Change
- `docs/guides/code_check.md` — the `rubycritic` row in the config table; drop the "not yet" note.
- `docs/guides/code_check/rubycritic.md` — the Configuration file section, `--no-config`, the header, errors and limitations.
