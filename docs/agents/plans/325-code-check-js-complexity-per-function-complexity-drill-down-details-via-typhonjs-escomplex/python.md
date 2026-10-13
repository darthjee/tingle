# Python Plan: code_check js_complexity: per-function complexity drill-down (--details) via typhonjs-escomplex

Main plan: [plan.md](plan.md)

## Shared contracts

The Python side consumes `FileResult.functions` (`None` or a list of `{name, line, cyclo, sloc}` dicts) and the `escomplex` warnings, both already parsed by `output_parser.py`. It owns the `--details` flag, `DEFAULT_DETAILS`, the `details` config key and the output formats listed in [plan.md](plan.md#shared-contracts). The spec, [`docs/agents/specs/code_check/js_complexity/details.md`](../../../../docs/agents/specs/code_check/js_complexity/details.md) §4–§8, is authoritative.

## Steps

- [01 — Flag, constant and config key](python/01-flag-and-config.md)
- [02 — Reporter function lines](python/02-reporter.md)
- [03 — Executor wiring, warning and long help](python/03-executor.md)

## CI Checks
- `python`: `ruff check .` and `pytest`, run from `python/` (CircleCI: Lint, Tests)

## Notes
- Mirror `code_check/rubycritic`, but **don't** copy `_check_methods`. Missing per-function data is not an error here (spec §5).
- Sorting differs from rubycritic: sort by `cyclo` descending, then `line`, then `name`, in the reporter.
