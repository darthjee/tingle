# Issue: Codacy: Method _flags has 55 lines of code (limit is 50) (python/check_file_size/executor.py:46)

## Description
Codacy's Lizard flagged `python/check_file_size/executor.py:46` (pattern `Lizard_nloc-medium`, category Complexity, severity Warning): "Method _flags has 55 lines of code (limit is 50)"

## Problem
`CheckFileSize._flags()` returns one long list literal of flag definitions for `ArgParser`, which pushes the method past Lizard's 50-line limit. The warning grew after #185 added the `--fail-on` CI flag.

## Expected Behavior
No function in `python/check_file_size/executor.py` exceeds 50 lines of code, and the CLI flags, defaults and `--help` output of `tingle check_file_size` are unchanged.

## Solution
Replace the `_flags()` static method with a module-level constant list `FLAGS` in `python/check_file_size/executor.py`, holding the same flag definitions in the same order. Lizard only measures functions, so a module-level list does not count against the limit. `CheckFileSize.run()` builds its parser with `ArgParser(FLAGS)`.

- Remove `_flags()` entirely (it has no callers besides `run()` and no direct tests).
- Update the docstring of `_sample_flags()` in `python/tests/common/test_arg_parser.py`, which currently says it mirrors `check_file_size._flags()`, to reference `FLAGS`.
- Existing tests under `python/tests/check_file_size/` and `python/tests/common/` must still pass.

## Benefits
Clears a Warning-level finding and makes the flag list easier to scan and extend.
