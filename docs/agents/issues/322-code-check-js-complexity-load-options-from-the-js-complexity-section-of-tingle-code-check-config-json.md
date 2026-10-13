# Issue: code_check js_complexity: load options from the js_complexity section of ~/.tingle/code_check/config.json

## Description
Load `tingle code_check js_complexity` options from a `js_complexity` section of `~/.tingle/code_check/config.json` (parent #315), with the same rules as `rubycritic`, and add the `--no-config` flag.

Spec: `docs/agents/specs/code_check/js_complexity/config.md` (normative).

## Problem
Every run has to repeat the thresholds, excludes and gate level on the command line. Today `python/code_check/js_complexity/executor.py` stubs the config out: it overrides `_load_config` to never read the file and `_parse_args` to fake `no_config=False`.

## Expected Behavior
- The section `js_complexity` is read with `code_check.config.load_section` through `DockerCheck._load_config`, with `SCHEMA`/`validate` in a new `python/code_check/js_complexity/config.py` built from `code_check.validators` (mirroring `rubycritic/config.py`):
  - `warn`, `error`, `critical`: `non_negative_number`
  - `top`: `non_negative_int`
  - `exclude`, `ignore`, `include`: `list_of_str`
  - `no_default_excludes`, `gitignore`: `boolean`
  - `fail_on`: `warn|error|critical`, nullable
  - `min_level`: `ok|warn|error|critical`
  - `image`: `non_empty_str`
- **No `ext` key.** `ext`, and any other unknown key (including `details` until #325 adds it), is an error.
- **Rules** (`DockerCheck._merge`):
  - Single values: built-in default < config < CLI; a config `null` means unset.
  - Lists (`exclude`, `ignore`, `include`): config list first, then the CLI list, deduplicated keeping the first occurrence.
  - `--no-default-excludes` / `--no-gitignore` can only turn behaviour off and win over the config.
  - The default image (and `shell/linux/VERSION`) is only read when neither `--image` nor `image` is set.
  - A missing file, a missing section or an empty section is fine; `Config: <path>` is shown in the header only when a section was loaded.
  - Invalid JSON, an unknown key or a wrong type prints `Error: <path>: <reason>` on stderr and exits 1, before any file selection or Docker call.
  - `--no-config` (new flag) skips the file: it is not read or validated.
  - Existing `file_size`/`rubycritic` sections are unaffected and ignored by `js_complexity`.
- Docs: `long_help` in `commands/python.json`, the executor module docstring, the `js_complexity` row of the "Configuration file" table, and a "Configuration file" section with an example in `docs/guides/code_check/js_complexity.md`.
- Tests under `python/tests/code_check/js_complexity/` cover every key's valid/invalid values, each precedence rule, list merging and dedup, `--no-config` with a broken file, missing file/section, empty section, `image` from config avoiding the `VERSION` read, and a file with only other sections.

## Solution
Add `js_complexity/config.py`, wire `validate_config` / `_load_section` into the executor like `rubycritic/executor.py`, add the `--no-config` flag, and remove the temporary `_load_config` and `_parse_args` overrides. The shared scaffolding in `docker_check` (#317) already does the loading and merging.

The dependency on the file selection sub-issue (#321) is met: it is merged, so every key already exists.

### Agents
- `python`: the schema, wiring, flag and tests.
- `cli`: `long_help` / flag listing in `commands/python.json` if it owns that file.
- `guide`: the guide section.

## Benefits
- Per-user defaults, with the same behaviour as the other `code_check` subcommands.
