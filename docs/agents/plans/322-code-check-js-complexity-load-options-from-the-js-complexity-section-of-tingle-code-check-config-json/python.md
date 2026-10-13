# Python Plan: code_check js_complexity: load options from the js_complexity section of ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

- Section `js_complexity`, keys and validators exactly as spec §2 (all rows marked #322; **no** `details`, **no** `ext`).
- `--no-config` flag: `{"name": "--no-config", "action": "store_true", "help": "Do not read ~/.tingle/code_check/config.json"}`, last in `FLAGS` (as in rubycritic).
- Precedence/merge, error reasons and the `Config:` header line come from `DockerCheck` unchanged; do not reimplement them.

## Steps

- [01 — Add the js_complexity config schema](python/01-add-config-schema.md)
- [02 — Add the --no-config flag](python/02-add-no-config-flag.md)
- [03 — Wire the config into the executor](python/03-wire-executor.md)
- [04 — Tests](python/04-tests.md)

## CI Checks
- `python/`: `ruff check .` and `pytest` (from `python/`; CI jobs in `.circleci/config.yml`).

## Notes
- `LIST_KEYS` stays `("ignore", "include")`; `exclude` is merged by `DockerCheck._merge` separately (same as rubycritic).
- `details` must stay an unknown key — #325 adds it later. Do not copy it from `rubycritic/config.py`.
- `code_check/completion.py` reads `FLAGS`, so `--no-config` completion comes for free; check the completion tests still pass (update any expected flag list).
