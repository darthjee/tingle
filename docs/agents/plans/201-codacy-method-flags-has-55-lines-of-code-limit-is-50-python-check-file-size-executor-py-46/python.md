# Python Plan: Codacy: Method _flags has 55 lines of code (limit is 50) (python/check_file_size/executor.py:46)

Main plan: [plan.md](plan.md)

## Overview
Lizard (`Lizard_nloc-medium`) flags `CheckFileSize._flags()` because the list
literal it returns is 55 lines long. Lizard only measures functions, so moving
the same list to module level clears the finding without changing behaviour.

## Context
`_flags()` is only called from `CheckFileSize.run()` (`ArgParser(self._flags())`)
and has no direct tests. `python/tests/common/test_arg_parser.py::_sample_flags`
has a docstring saying it mirrors `check_file_size._flags()`.

## Implementation Steps

### Step 1 — Move the flag list to a module-level `FLAGS` constant
In `python/check_file_size/executor.py`:
- Add a module-level `FLAGS: list[dict] = [...]` after the imports and before
  `class CheckFileSize`, with a short comment or docstring-style comment
  ("Flag definitions for ArgParser."). Copy the eight entries verbatim and in
  the same order (`path`, `--warn`, `--error`, `--critical`, `--top`,
  `--exclude`, `--ext`, `--fail-on`), keeping every `type`, `default`,
  `choices`, `action` and `help` value (including the f-strings that use
  `Constants`) exactly the same.
- Delete the `_flags()` static method.
- In `run()`, change `ArgParser(self._flags())` to `ArgParser(FLAGS)`.

Because `ArgParser` does not mutate the flag dicts (check
`python/common/arg_parser.py` to confirm), sharing one module-level list is
safe. If it turns out it does mutate them, pass a copy instead
(`ArgParser([dict(f) for f in FLAGS])`).

### Step 2 — Update the test docstring reference
In `python/tests/common/test_arg_parser.py`, change the `_sample_flags()`
docstring from "mirroring check_file_size._flags()" to reference
`check_file_size.executor.FLAGS`. No test logic changes.

## Files to Change
- `python/check_file_size/executor.py` — add module-level `FLAGS`, remove
  `_flags()`, use `FLAGS` in `run()`.
- `python/tests/common/test_arg_parser.py` — docstring reference only.

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- Verify `--help` output is byte-identical before and after, e.g. compare
  `python3 python/check_file_size/executor.py --help` (or the `main.py` entry
  point) output against `main`.
- No function in `executor.py` should exceed 50 lines of code afterwards;
  `run()` is currently about 60 physical lines including comments/blank lines, but
  Lizard counts NLOC (no blanks/comments). If a local `lizard` run is
  available, confirm `run()` stays under the limit. Splitting `run()` is out of
  scope unless it is also flagged.
