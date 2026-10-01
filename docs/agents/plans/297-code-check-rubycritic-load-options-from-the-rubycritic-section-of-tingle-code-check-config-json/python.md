# Python Plan: code_check rubycritic: load options from the rubycritic section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

The `python` agent produces the behaviour described in [plan.md](plan.md#shared-contracts):

- the `--no-config` flag (last in `FLAGS`, help `Do not read ~/.tingle/code_check/config.json`);
- the `rubycritic` section keys, their validation reasons and defaults;
- the precedence rules;
- the `Config: <path>` header line;
- `Error: <path>: <reason>` + exit 1 for config errors.

The reason strings must match the table in [config.md §2](../../specs/code_check/rubycritic/config.md#2-keys) word for word.

## Steps

- [01 — Move the shared validators](python/01-shared-validators.md)
- [02 — Add rubycritic/config.py](python/02-rubycritic-config.md)
- [03 — Wire the config into the flags and executor](python/03-wire-executor.md)
- [04 — Tests](python/04-tests.md)

## CI Checks
- `python/`: `ruff check .` (CI job: lint), from `python/`
- `python/`: `pytest` (CI job: tests), from `python/`

## Notes
- `rubycritic/flags.py` must stay cheap to import: `code_check.completion` imports it. Do not import `code_check.config`, `code_check.validators` or `rubycritic/config.py` from `flags.py`. `test_completion_imports_no_heavy_module` already lists `code_check.config`; add `code_check.rubycritic.config` to that list.
- `rubycritic` has no legacy section, so `_load_config` is simpler than `file_size`'s: one `load_section("rubycritic", path)` call.
- The CLI `_validate` checks (negative/NaN thresholds, negative `--top`/`--details`, empty `--image`) stay as they are. They still apply to CLI values. Config values are already validated by `validate`, so running them again after the merge is harmless.
- Specs under `docs/agents/specs/code_check/rubycritic/` are removed later by #298; do not touch them here.
