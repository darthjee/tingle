# Python Plan: code_check js_complexity: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

You produce the five flags exactly as in the table in [plan.md](plan.md#shared-contracts): names, argparse shapes, dests, help texts, and their order after `--image`. The `cli` and `guide` agents describe that behaviour in their own words.

## Steps

- [01 — Add the selection flags](python/01-add-flags.md)
- [02 — Wire the flags in the executor](python/02-wire-executor.md)
- [03 — Tests](python/03-tests.md)

## CI Checks
- `python/`: `cd python && ruff check . && pytest` (CI jobs: `lint`, `tests`)

## Notes
- Don't touch `docker_check`, `file_size`, `rubycritic` or `code_check.excludes`. Their tests must pass unchanged.
- Keep the `_parse` and `_load_config` overrides: they belong to #322.
