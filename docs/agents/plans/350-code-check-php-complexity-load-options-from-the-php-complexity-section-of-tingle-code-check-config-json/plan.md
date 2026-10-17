# Plan: code_check php_complexity: load options from the php_complexity section of ~/.tingle/code_check/config.json

Issue: [350-code-check-php-complexity-load-options-from-the-php-complexity-section-of-tingle-code-check-config-json.md](../../issues/350-code-check-php-complexity-load-options-from-the-php-complexity-section-of-tingle-code-check-config-json.md)

## Overview
Replace the stub `php_complexity` config schema with the real one (`js_complexity`'s keys minus `details`), remove the executor overrides that skip the config file, and add the `--no-config` flag, so `DockerCheck` loads, validates and merges the `php_complexity` section like it does for `js_complexity`. The normative rules are in `docs/agents/specs/code_check/php_complexity/config.md`. Help text, user guides and architecture docs are updated in the same PR.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Config file:** `~/.tingle/code_check/config.json`, section `"php_complexity"` (`CONFIG_SECTION`, already defined in the executor).
- **Keys (exactly these 12, before #351):** `warn`, `error`, `critical` (number >= 0); `top` (integer >= 0); `exclude`, `ignore`, `include` (list of strings); `no_default_excludes`, `gitignore` (boolean); `fail_on` (`warn|error|critical` or `null`); `min_level` (`ok|warn|error|critical`); `image` (non-empty string). `ext` and `details` are unknown keys and exit 1.
- **New flag:** `--no-config` (`store_true`, help `"Do not read ~/.tingle/code_check/config.json"`), appended last in `FLAGS`, after `--include`.
- **Precedence:** single values: built-in default < config < CLI (config `null` = unset). Lists: config first, then CLI, deduplicated, default excludes in front unless `no_default_excludes`. `--no-default-excludes`/`--no-gitignore` win. `gitignore` defaults to true.
- **Errors:** `Error: <path>: <reason>` in red on stderr, exit 1, before selection or Docker. Reasons are the spec's §2/§5 table (for example, `unknown key 'ext'`).
- **Header:** `Config: <config file>` (dim) when a section was loaded, including an empty one.
- **Exit 1 list** in help/guides gains "invalid config file".
