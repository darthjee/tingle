# Unit tests: FileAnalyzer

Cover `python/check_file_size/file_analyzer.py`'s `count_lines()`,
`classify()`, and `format_number()`.

Cases:
- `count_lines()` on a real `tmp_path` file returns the exact line count
  (including a file with no trailing newline, and an empty file → 0).
- `count_lines()` returns `-1` for a missing path (`OSError`).
- `count_lines()` returns `-1` for a permission-denied path (`chmod 000`,
  `PermissionError`) — only meaningful under the non-root container (step
  03); note this explicitly in the test (e.g. skip/xfail with a clear reason
  if `os.geteuid() == 0`, as a defensive fallback for anyone running the
  suite outside Docker as root).
- `classify(lines)` boundary behavior against configurable
  `warn`/`error`/`critical` thresholds: exactly at each threshold and one
  below each — confirms `>=` semantics (`lines >= critical` →
  `🟣 CRITICAL`, down to `✅ OK` below `warn`).
- `format_number()` inserts `.` as the thousands separator (e.g. `1234` →
  `"1.234"`), matching the existing `,` → `.` replace behavior.

## Files to Change

- `python/tests/check_file_size/test_file_analyzer.py` — new, cases above.
