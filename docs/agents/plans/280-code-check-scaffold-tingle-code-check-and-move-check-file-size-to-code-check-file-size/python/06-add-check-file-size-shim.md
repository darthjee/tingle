# Add the check_file_size shim
Reduce `python/check_file_size/` to `__init__.py` and `main.py` (keep 100755). `main.py` inserts `python/` into
`sys.path` and, on `flow == "run"`, calls `code_check.file_size.executor.CheckFileSize().run(sys.argv[2:])`. It prints
no warning; that comes in a later sub-issue of #279. Do **not** add a `completion.py` or a `complete` branch here, so
the alias keeps today's file/folder completion fallback.

Tests: write `python/tests/check_file_size/test_main.py`, monkeypatching `CheckFileSize` as it is referenced from the
shim module. Check that `run` forwards `sys.argv[2:]` unchanged and that nothing is written to stderr. Keep
`tests/check_file_size/__init__.py` and `conftest.py`. Finally run `cd python && ruff check . && pytest`, confirm
coverage is at or above 75%, and compare `bin/tingle code_check file_size .` with `bin/tingle check_file_size .`
(stdout, stderr and exit code).

## Files to Change
- `python/check_file_size/main.py` — shim forwarding to `code_check.file_size.executor.CheckFileSize`.
- `python/tests/check_file_size/test_main.py` — shim test.
