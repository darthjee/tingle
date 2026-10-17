# Python Plan: code_check php_complexity: load options from the php_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- `SCHEMA` in `python/code_check/php_complexity/config.py` holds exactly the 12 keys in the main plan, with `js_complexity`'s validators; no `details` (#351) and no `ext`.
- `FLAGS` gains `--no-config` (`store_true`, help `"Do not read ~/.tingle/code_check/config.json"`) as its last entry; completion picks it up from `FLAGS`.
- Behaviour follows `docs/agents/specs/code_check/php_complexity/config.md` §1–§5.

## Steps

- [01 — Real config schema](python/01-config-schema.md)
- [02 — Executor and --no-config flag](python/02-executor-and-flag.md)
- [03 — Tests](python/03-tests.md)

## CI Checks
- `python/`: `cd python && ruff check .` (CI job: `lint`)
- `python/`: `cd python && pytest` (CI job: `tests`)

## Notes
- Mirror `js_complexity` closely: `config.py`, the `--no-config` flag entry and `tests/code_check/js_complexity/test_config.py` / `test_executor_config.py` are the templates.
- `DockerCheck._load_config` and `DockerCheck._parse` already implement loading, `--no-config` and the merge; the work is mostly deleting the overrides.
- `image` from the config must avoid the `shell/linux/VERSION` read; check that the existing `resolve_image` path already does this, as in `js_complexity`.
