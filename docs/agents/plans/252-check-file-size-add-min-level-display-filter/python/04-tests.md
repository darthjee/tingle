# Tests
- `test_file_analyzer.py`: `reaches(n, "ok")` is `True` for 0, small and very large counts.
- `test_reporter.py`: the summary counts and `Total:` use the full results when `shown` is a subset; with `shown=[]` it prints `No files at or above WARN.` and no `Status`/`Lines` header; `shown=None` keeps the current output.
- `test_executor.py`:
  - `--min-level warn` hides OK rows and shows WARN or higher.
  - `--min-level error --top 1` shows the largest ERROR-or-higher row, not the largest overall.
  - `--top 1` summary still counts every file (e.g. `2 file(s)`).
  - `--min-level critical --fail-on warn` exits `2` even when the offending rows are hidden.
  - With nothing at or above the level, the note is printed and the exit code is `0`.
  - `--min-level foo` exits `1`.
  - `--min-level ok` output equals the output without the flag.

## Files to Change
- `python/tests/check_file_size/test_file_analyzer.py`
- `python/tests/check_file_size/test_reporter.py`
- `python/tests/check_file_size/test_executor.py`
