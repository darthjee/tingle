# Plan: check_file_size: load options from ~/.tingle/code_check/config.json

Issue: [253-check-file-size-load-options-from-tingle-code-check-config-json.md](../../issues/253-check-file-size-load-options-from-tingle-code-check-config-json.md)

## Overview
Add a user config file, `~/.tingle/code_check/config.json`, whose `check_file_size` section provides defaults for every `check_file_size` option. A generic loader plus a strict validator go in a new `python/check_file_size/config.py`. `executor.py` merges the config with the CLI (for single values the CLI wins, lists are concatenated, the CLI booleans only turn behaviour off). Two additions beyond the original spec: a `--no-config` escape hatch, and a dim `Config: <path>` header line. The spec files, `long_help` and the user guide are updated in the same PR.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Location**: `Path.home() / ".tingle" / "code_check" / "config.json"` (honours `HOME`). No flag to change it.
- **Section**: top-level JSON object; key `check_file_size`. Other top-level keys are ignored.
- **Keys** (all optional):

  | Key | Type | CLI flag |
  |-----|------|----------|
  | `warn`, `error`, `critical`, `top` | int >= 0 (JSON bool rejected) | `--warn`, `--error`, `--critical`, `--top` |
  | `exclude`, `ignore`, `include`, `ext` | list of str | `--exclude a,b`, `--ignore`, `--include`, `--ext` |
  | `no_default_excludes` | bool (default `false`) | `--no-default-excludes` |
  | `gitignore` | bool (default `true`) | `--no-gitignore` (inverted) |
  | `fail_on` | `"warn"` \| `"error"` \| `"critical"` \| `null` | `--fail-on` |
  | `min_level` | `"ok"` \| `"warn"` \| `"error"` \| `"critical"` | `--min-level` |

- **Precedence**: single values: built-in defaults < config < CLI. Lists: config then CLI, concatenated, deduplicated (first occurrence kept). Booleans: the config sets either value; `--no-default-excludes` / `--no-gitignore` only turn behaviour off and win.
- **New flag** `--no-config` (`store_true`): the config file is not read or validated at all.
- **Header**: when a `check_file_size` section was loaded, even an empty one (file exists and has the key), print a dim `Config: <config path>` line right after the `Thresholds:` line (before the blank line). Nothing when the file/section is missing or `--no-config` is given.
- **Errors**: `Error: <config path>: <reason>` on stderr (red via `Palette(sys.stderr)`), exit 1, before any stdout output. Reasons: invalid JSON / unreadable file, top level not an object, section not an object, `unknown key '<k>'` (including `path`), wrong type/value (e.g. `'top' must be an integer >= 0`, `'fail_on' must be one of warn, error, critical or null`).
- `tingle check_file_size` with no args prints help and exits 0 without reading the config.
- Out of scope: threshold ordering checks, project-level config, the `code_check` migration.
