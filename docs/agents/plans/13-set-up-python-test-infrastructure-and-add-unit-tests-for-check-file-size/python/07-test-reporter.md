# Unit tests: Reporter

Cover `python/check_file_size/reporter.py`'s `Reporter.report()`, using
`capsys` to assert on printed output and a real (or minimally mocked)
`FileAnalyzer` for `classify()`/`format_number()`.

Cases:
- Given a mixed list of `(path, lines)` results spanning OK/WARN/ERROR/
  CRITICAL, `report()` prints one row per result and a summary line whose
  per-category counts match exactly (e.g. `2 OK`, `1 WARN`).
- `Total:` reflects the sum of all result line counts, formatted via
  `format_number()`.
- Empty `results` list: prints headers and a summary with all counts at 0
  and `Total: 0`, without raising.
- `display_path` resolution: relative to `target.parent` when `target` is a
  directory, vs. `path.name` alone when `target` is a single file — cover
  both branches, plus the `ValueError` fallback (`path` not relative to
  `target.parent`) falling back to `str(path)`.

## Files to Change

- `python/tests/check_file_size/test_reporter.py` — new, cases above.
