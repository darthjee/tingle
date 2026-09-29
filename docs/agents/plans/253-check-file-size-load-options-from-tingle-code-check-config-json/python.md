# Python Plan: check_file_size: load options from ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

Implements every contract in [plan.md](plan.md#shared-contracts): config location, schema, precedence, `--no-config`, the `Config:` header line and the error format. The `cli` and `guide` agents document exactly this behaviour, so flag help text and error strings must match the contract.

## Steps

- [01 — Isolate HOME in tests](python/01-isolate-home-in-tests.md)
- [02 — Add config.py loader and validator](python/02-add-config-module.md)
- [03 — Merge config into executor](python/03-merge-config-into-executor.md)
- [04 — Tests](python/04-tests.md)

## CI Checks
- `python`: `cd python && ruff check . && pytest` (CI jobs: Lint, Tests)

## Notes
- JSON `true`/`false` are Python `bool`, a subclass of `int`: integer validators must reject `bool` explicitly.
- `--ext` with an empty merged list must still mean "no filter" (`FileCollector` already treats `[]`/`None` the same).
- Keep `load_section` free of `check_file_size` knowledge so the future `code_check` tool can reuse it.
