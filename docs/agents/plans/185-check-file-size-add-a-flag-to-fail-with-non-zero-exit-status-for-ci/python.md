# Python Plan: check_file_size: add a flag to fail with non-zero exit status for CI

Main plan: [plan.md](plan.md)

## Shared contracts

Produce exactly the flag, gate semantics, exit codes (0/1/2), stream and
colour rules described in [plan.md](plan.md#shared-contracts). `bin/tingle`
already `exec`s the script, so the exit status reaches the caller unchanged.
No `cli` work is needed.

## Steps

- [01 — TTY/NO_COLOR-aware colours](python/01-tty-aware-colours.md)
- [02 — Errors to stderr, usage errors exit 1](python/02-errors-to-stderr.md)
- [03 — Add the --fail-on gate](python/03-fail-on-gate.md)
- [04 — Update long_help](python/04-long-help.md)

## CI Checks
- `python`: `cd python && ruff check .` (CI job: python lint)
- `python`: `cd python && pytest` (CI job: python tests)

## Notes
- `Constants` colour codes are class attributes read at call time throughout
  `reporter.py`, `file_analyzer.py` and `executor.py`. Keep the raw codes in
  `Constants` and add a stream-aware accessor. Don't mutate `Constants`
  globally, because that would leak between tests.
- Existing tests that assert on stdout for the path-not-found error
  (`test_executor.py`) must be updated to read stderr.
- Remapping argparse usage errors from 2 to 1 is local to `check_file_size`.
  Do not change `common/arg_parser.py` behaviour for other commands (e.g. `kube`).
