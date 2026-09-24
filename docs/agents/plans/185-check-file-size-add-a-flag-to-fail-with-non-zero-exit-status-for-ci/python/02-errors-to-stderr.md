# Errors to stderr, usage errors exit 1
- Print `Error: path not found: <target>` to `sys.stderr` (coloured with the
  stderr palette from step 01) and keep `sys.exit(1)`.
- argparse already writes usage errors to stderr but exits with 2. In
  `CheckFileSize.run`, wrap `arg_parser.parse(args)` so that a `SystemExit`
  with a non-zero code (argparse error) is re-raised as `SystemExit(1)`.
  `--help` (code 0) must still exit 0. Keep this local to `check_file_size`;
  don't change `common/arg_parser.py`.

Tests: path-not-found message is on stderr (not stdout) with exit 1.
`--top abc` exits 1. `--help` still exits 0.

## Files to Change
- `python/check_file_size/executor.py`: stderr error, usage-error exit remap
- `python/tests/check_file_size/test_executor.py`: update the path-not-found test to read stderr; add usage-error tests
