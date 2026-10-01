# Issue: code_check rubycritic: load options from the rubycritic section of ~/.tingle/code_check/config.json

## Description
Let `tingle code_check rubycritic` read its defaults from a `rubycritic` section in `~/.tingle/code_check/config.json` (parent #290), the file `file_size` already uses. The full contract is in [docs/agents/specs/code_check/rubycritic/config.md](../specs/code_check/rubycritic/config.md); this issue implements it.

## Problem
Today `rubycritic` only takes options from the command line, and `docs/guides/code_check.md` says it does not read the config file yet. Users who always pass the same thresholds, excludes or image have to repeat them on every run, while `file_size` already supports personal defaults.

## Expected Behavior
- The `rubycritic` section is loaded with the generic `code_check.config.load_section("rubycritic")`. Other sections are ignored, and there is no legacy section name.
- Keys: `warn`, `error`, `critical` (finite numbers ≥ 0, floats allowed, booleans/`NaN`/`Infinity` rejected), `top` (int ≥ 0), `exclude`, `ignore`, `include` (lists of strings), `no_default_excludes`, `gitignore` (booleans), `fail_on` (`warn`/`error`/`critical`/`null`), `min_level` (`ok`/`warn`/`error`/`critical`), `image` (non-empty string after trimming) and `details` (int ≥ 0 or `null`). There is **no** `ext`: `"ext"` is an unknown key.
- Precedence:
  - Single values: built-in default < config < CLI.
  - Lists: the config list comes first, then the CLI list. They are concatenated and deduplicated, with the default excludes added in front unless `no_default_excludes` is true.
  - `--no-default-excludes` and `--no-gitignore` can only turn behaviour off, and they win over the config.
- The default image (and the `shell/linux/VERSION` read) is only computed when neither `--image` nor the config `image` is set.
- A missing file or a missing section is fine: built-in defaults apply and no `Config:` line is printed. An empty section is valid and prints `Config: <path>` (dim) in the header.
- An unreadable file, invalid JSON, a non-object top level or section, an unknown key or a wrong type prints `Error: <path>: <reason>` in red on stderr and exits 1, before any file selection or Docker call. The reasons use `file_size`'s wording.
- A new `--no-config` flag skips reading and validating the file.

## Solution
- Add `python/code_check/rubycritic/config.py` with `SCHEMA` and `validate(section, path)`, structured like `file_size/config.py`. Reuse `file_size`'s validators instead of copying them. Moving them to a shared module is allowed if `file_size`'s messages and behaviour stay the same. Add a `_non_negative_number` validator for the thresholds and validators for `image` and `details`.
- Add `--no-config` to `rubycritic/flags.py`. In `rubycritic/executor.py`, load the config and merge it as `CheckFileSize._merge` does, before the existing CLI validation, the default-image resolution and the file selection.
- Docs:
  - `long_help` in `commands/python.json` and the executor module docstring.
  - The `rubycritic` row of the "Configuration file" table in `docs/guides/code_check.md`, replacing the "does not read the config file yet" note.
  - A configuration section in `docs/guides/code_check/rubycritic.md`.
- Tests under `python/tests/code_check/rubycritic/`, covering:
  - Every key's valid and invalid values.
  - Each precedence rule, and list merging with deduplication.
  - `--no-config` with a broken file.
  - A missing file, a missing section and an empty section.
  - A config `image` avoiding the `VERSION` read.

## Depends on
#296 (file selection flags) and #291 (`--details`); both are merged.

## Agents
- `python`: config module, flags, executor, tests.
- `cli`: `long_help` in `commands/python.json`.
- `guide`: `docs/guides/code_check.md` and `docs/guides/code_check/rubycritic.md`.

## Benefits
`rubycritic` gets the same personal defaults as `file_size`, from one shared config file, so users don't have to repeat flags on every run.
