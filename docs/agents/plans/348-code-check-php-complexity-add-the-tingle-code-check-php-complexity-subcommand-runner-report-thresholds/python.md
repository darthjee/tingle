# Python Plan: code_check php_complexity: add the tingle code_check php_complexity subcommand (runner, report, thresholds)

Main plan: [plan.md](plan.md)

## Shared contracts

Produces everything in [plan.md § Shared contracts](plan.md#shared-contracts): the subcommand name and registration, the flags, levels, report layout, selection and exit codes. Builds against [`cli.md`](../../specs/code_check/php_complexity/cli.md) and does not change `python/code_check/docker_check/`. The `cli` agent owns `commands/python.json`. This agent owns `python/code_check/completion.py`.

## Steps

- [01 — Package skeleton and bindings](python/01-package-skeleton.md)
- [02 — Output parser](python/02-output-parser.md)
- [03 — Reporter](python/03-reporter.md)
- [04 — Executor and registration](python/04-executor-registration.md)

## CI Checks
- `python/`: `cd python && ruff check . && pytest` (CI jobs: `lint`, `tests`), or `make tests`.

## Notes
- Copy the `js_complexity` module and test layout from #320 (commit `d098b62`). Diff against it so the only differences are the PHP-specific parts.
- `config.py` is a stub that accepts nothing until #350, the same as `js_complexity` before #322.
- Build the sample JSON in the tests from the fixture under `docker/php_complexity/fixture`. The cli.md §6 example shows the expected output.
- For the manual end-to-end check, run `make php-complexity-image`, then `tingle code_check php_complexity --image tingle_php_complexity:dev docker/php_complexity/fixture`.
