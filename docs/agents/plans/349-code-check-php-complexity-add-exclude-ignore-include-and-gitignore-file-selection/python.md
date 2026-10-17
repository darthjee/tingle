# Python Plan: code_check php_complexity: add --exclude/--ignore/--include and .gitignore file selection

Main plan: [plan.md](plan.md)

## Shared contracts

The python agent produces the five flags in `FLAGS`, with the exact names, argparse settings and help texts in the [plan.md](plan.md#shared-contracts) table. `code_check.completion` and the `--help` output derive from them. It also makes the executor behave as listed there. The cli agent's `long_help` and the guide agent's guide describe that same behaviour.

## Steps

- [01 — Declare the selection flags](python/01-declare-flags.md)
- [02 — Use the merged selection options in the executor](python/02-executor-selection-options.md)
- [03 — Tests](python/03-tests.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`), or `docker-compose run --rm tingle_tests pytest`

## Notes
- `DockerCheck._merge` already parses `--exclude` through `parse_excludes` (which splits on commas and drops blank entries) and maps `no_gitignore` to `gitignore`. No change is needed there: `_merge` works without a config, because `_load_config` still returns `{}` until #350.
- Keep the `_parse`/`_load_config` overrides: removing them is #350's job.
- `file_size`, `rubycritic` and `js_complexity` selection tests must pass unchanged.
