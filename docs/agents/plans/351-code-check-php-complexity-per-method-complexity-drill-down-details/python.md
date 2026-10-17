# Python Plan: code_check php_complexity: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

The CLI can rely on `FileResult.functions` (already parsed and validated by `output_parser.py`) being `None`, `[]`, or a list of `{"name": str, "line": int, "ccn": int, "npath": int}` dicts. `--details`: `int`, `nargs="?"`, `const=5`, default `None`. Config key `details`: `nullable_non_negative_int`.

## Steps

- [01 — Add the flag, constant and config key](python/01-flag-constant-config.md)
- [02 — Print the per-function lines in the reporter](python/02-reporter-function-lines.md)
- [03 — Wire the executor and update the long help](python/03-executor-wiring.md)

## CI Checks
- `python`: run the code_check test suite (e.g. `cd python && python -m pytest tests/code_check`) plus the repo's Python lint (CI jobs in `.circleci/config.yml`).

## Notes
- The negative-value check already exists in `DockerCheck._validate` (`docker_check/executor.py`). It runs as soon as `"details"` is in `SINGLE_DEFAULTS`, so no new validation code is needed, only a test.
- Completion derives value flags from `FLAGS` (`completion.py`), so `--details` is picked up automatically. Add or adjust a completion test that asserts `--details` is a free-form value flag for `php_complexity`.
- `output_parser.py` already validates `functions`. Leave it unchanged unless a test shows that a large `npath` is not kept exact.
