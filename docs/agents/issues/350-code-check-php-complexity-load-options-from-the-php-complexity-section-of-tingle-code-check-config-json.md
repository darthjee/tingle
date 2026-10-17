# Issue: code_check php_complexity: load options from the php_complexity section of ~/.tingle/code_check/config.json

## Description
Load `tingle code_check php_complexity` options from the `php_complexity` section of `~/.tingle/code_check/config.json` (parent #344), the same way the `rubycritic` and `js_complexity` sections work.

**Normative spec:** `docs/agents/specs/code_check/php_complexity/config.md`.

The file selection sub-issue (#349) has landed, so every key already exists. Today `python/code_check/php_complexity/config.py` is a stub with an empty `SCHEMA`, and the executor overrides `_load_config` and `parse_args` so that the file is never read and `no_config` is always `False`.

## Problem
`php_complexity` is the only `code_check` subcommand that ignores the config file. Users must pass the thresholds, selection and image flags on every run, and there is no `--no-config` flag.

## Expected Behavior
- The section is read with `code_check.config.load_section("php_complexity")` through `DockerCheck._load_config`. The stub overrides of `_load_config` and `parse_args` in `python/code_check/php_complexity/executor.py` are removed.
- `SCHEMA`/`validate` in `python/code_check/php_complexity/config.py` are built from `code_check.validators`, exactly like `js_complexity/config.py`, minus `details`.
- **Keys:**
  - `warn`, `error`, `critical`: `non_negative_number`
  - `top`: `non_negative_int`
  - `exclude`, `ignore`, `include`: `list_of_str`
  - `no_default_excludes`, `gitignore`: `boolean`
  - `fail_on`: `warn|error|critical`, nullable
  - `min_level`: `ok|warn|error|critical`
  - `image`: `non_empty_str`
- **No `ext` key:** it is reported as `unknown key 'ext'` and exits 1. `details` is also an unknown key until #351.
- **Rules (spec §3–§5):**
  - Single values: built-in default < config < CLI. A config `null` means unset.
  - Lists: config list first, then the CLI list, concatenated and deduplicated. Default excludes are added in front unless `no_default_excludes` resolves to true.
  - `--no-default-excludes`/`--no-gitignore` can only turn behaviour off, and they win over the config.
  - `image` from the config means `shell/linux/VERSION` is not read.
  - A missing file or a missing section is fine (defaults, no `Config:` line). An empty section is valid and prints the `Config:` line.
  - Invalid JSON, an unknown key, a wrong type or a non-object section prints `Error: <path>: <reason>` in red on stderr and exits 1, before any file selection or Docker call.
  - A new `--no-config` flag (in `flags.py`) skips the file, which is not read or validated.
  - Existing files with only `file_size`/`rubycritic`/`js_complexity` sections stay valid and unchanged in meaning.
- **Docs:** the `long_help` in `commands/python.json` (a Configuration block, `--no-config`, the invalid-config exit 1 and an example), the executor and `config.py` docstrings, the `php_complexity` row of the "Configuration file" table in `docs/guides/code_check.md` (replacing "does not read this file yet"), and `docs/guides/code_check/php_complexity.md` with an example section.
- **Tests** under `python/tests/code_check/php_complexity/` cover everything listed in spec §7.

### Out of scope
- The `details` key (#351).
