# Plan: code_check rubycritic: load options from the rubycritic section of ~/.tingle/code_check/config.json

Issue: [297-code-check-rubycritic-load-options-from-the-rubycritic-section-of-tingle-code-check-config-json.md](../../issues/297-code-check-rubycritic-load-options-from-the-rubycritic-section-of-tingle-code-check-config-json.md)

## Overview
`tingle code_check rubycritic` starts reading its defaults from the `rubycritic` section of `~/.tingle/code_check/config.json`, using the `file_size` pattern: a per-subcommand `config.py` (`SCHEMA` + `validate`), a `_load_config` and `_merge` step in the executor, a `Config:` header line and a `--no-config` flag. The `file_size` validators move to a shared module so both subcommands use them. The `cli` and `guide` agents document the new behaviour. The full contract is [docs/agents/specs/code_check/rubycritic/config.md](../../specs/code_check/rubycritic/config.md).

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- **Config file:** `~/.tingle/code_check/config.json` (`code_check.config.default_path()`), section `"rubycritic"`. There is no legacy section name.
- **New flag:** `--no-config` (store_true). Help text: `Do not read ~/.tingle/code_check/config.json` (the same text as `file_size`). It goes last in `rubycritic/flags.py`'s `FLAGS`, after `--include`.
- **Keys** (flag names with `-` replaced by `_`):

  | Key | Type | Built-in default |
  |-----|------|------------------|
  | `warn`, `error`, `critical` | finite number ≥ 0 (int or float; booleans, NaN and Infinity rejected) | `100`, `200`, `400` |
  | `top` | int ≥ 0 | `0` |
  | `fail_on` | `"warn"` / `"error"` / `"critical"` / `null` | `null` |
  | `min_level` | `"ok"` / `"warn"` / `"error"` / `"critical"` | `"ok"` |
  | `image` | non-empty string after trimming | `darthjee/tingle_rubycritic:<tingle version>` |
  | `details` | int ≥ 0 or `null` (`0` = all methods) | `null` |
  | `exclude`, `ignore`, `include` | list of strings | `[]` |
  | `no_default_excludes` | boolean | `false` |
  | `gitignore` | boolean | `true` |

  There is **no** `ext` key; it is reported as `unknown key 'ext'`.
- **Precedence:**
  - Single values: built-in default < config < CLI.
  - Lists: the config list first, then the CLI list, concatenated and deduplicated (first occurrence wins). The default excludes are added in front unless `no_default_excludes` resolves to true.
  - `--no-default-excludes` and `--no-gitignore` only turn behaviour off, and they win over the config.
  - `--no-config`: the file is not read.
- **Output:**
  - When a section was loaded (even `{}`), the header prints `Config: <path>` (dim) after the `Image:` line.
  - Every config error prints `Error: <path>: <reason>` in red on stderr and exits 1, before any file selection or Docker call.
