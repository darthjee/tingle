# Plan: code_check js_complexity: load options from the js_complexity section of ~/.tingle/code_check/config.json

Issue: [322-code-check-js-complexity-load-options-from-the-js-complexity-section-of-tingle-code-check-config-json.md](../../issues/322-code-check-js-complexity-load-options-from-the-js-complexity-section-of-tingle-code-check-config-json.md)

Spec (normative): [config.md](../../specs/code_check/js_complexity/config.md)

## Overview
`tingle code_check js_complexity` starts reading its defaults from the `js_complexity` section of `~/.tingle/code_check/config.json` and gains a `--no-config` flag. All the loading/merging logic already lives in `DockerCheck` (`python/code_check/docker_check/executor.py`); this issue adds the section schema (`js_complexity/config.py`, a copy of `rubycritic/config.py` without `details`), wires it into the executor the way `rubycritic/executor.py` does, removes the two temporary stub overrides, and documents the feature.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- **Config file:** `~/.tingle/code_check/config.json`, section `"js_complexity"` (other sections ignored).
- **Keys** (flag names with `-` → `_`): `warn`, `error`, `critical` (number >= 0, decimals allowed), `top` (integer >= 0), `exclude`, `ignore`, `include` (JSON lists of strings), `no_default_excludes` (boolean), `gitignore` (boolean, default true — the inverse of `--no-gitignore`), `fail_on` (`warn|error|critical` or null), `min_level` (`ok|warn|error|critical`), `image` (non-empty string).
- **Not keys:** `ext` and `details` (until #325) are reported as `unknown key '<key>'`.
- **Precedence:** single values built-in default < config < CLI (config `null` = unset); lists config first then CLI, deduplicated; `--no-default-excludes` / `--no-gitignore` always win.
- **New flag:** `--no-config` — `store_true`, help text `Do not read ~/.tingle/code_check/config.json` (same as rubycritic).
- **Errors:** `Error: <path>: <reason>` on stderr, exit 1, before file selection or Docker. Reasons per spec §5.
- **Header:** `Config: <path>` (dim) only when a section was loaded.
- **Example for docs** (single source; reuse in long_help and the guide):

  ```json
  {"js_complexity": {"warn": 40, "exclude": ["generated"], "fail_on": "error"}}
  ```
