# Add prog to ArgParser
Give `ArgParser.__init__(self, flags, prog=None)` (`python/common/arg_parser.py:17`) an optional `prog` argument, and
pass it to `argparse.ArgumentParser(prog=prog)` in `build()` (L28). Leave it as `None` to keep today's default.
`CheckFileSize` builds `ArgParser(FLAGS, prog="tingle code_check file_size")` in `run()` (~L303).

Tests: in `tests/common/test_arg_parser.py`, add a case showing that `prog` appears in the help. In
`tests/code_check/file_size/test_executor.py`, assert that no-args help contains
`usage: tingle code_check file_size`. Today's help assertions only check that `"usage"` is present.

## Files to Change
- `python/common/arg_parser.py` — add the optional `prog`.
- `python/code_check/file_size/executor.py` — pass `prog`.
- `python/tests/common/test_arg_parser.py`, `python/tests/code_check/file_size/test_executor.py` — prog assertions.
