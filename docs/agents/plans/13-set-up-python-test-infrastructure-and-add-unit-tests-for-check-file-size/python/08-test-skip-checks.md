# Unit tests: SkipChecks

Cover `python/check_file_size/skip_checks.py`'s
`SkipChecks.is_binary_file()`, exactly the three detection paths in order.

Cases:
- Known binary extension (e.g. `.png`, from `Constants.BINARY_EXTENSIONS`)
  → `True`, without needing real file content (extension check short-
  circuits first).
- Content-based: a file with a null byte in the first 1024 bytes → `True`,
  even with a non-binary extension.
- Content-based: a file whose first 1024 bytes fail UTF-8 decoding (e.g.
  invalid continuation byte) → `True`.
- A plain UTF-8 text file with no null bytes and a non-binary extension →
  `False`.
- A file larger than 1024 bytes where the binary marker (null byte / bad
  UTF-8) only appears after the first 1024 bytes → `False` (only the first
  1024 bytes are inspected).
- Missing/permission-denied path → `True` (caught as `OSError`/
  `PermissionError`, treated as "skip it"); same non-root caveat as step 06
  — meaningful only under the non-root container, with the same defensive
  `os.geteuid()` fallback note.

Also cover the `check_file_size`-level edge cases the issue calls out that
live in `FileCollector`/`CheckFileSize` rather than `SkipChecks` itself:
- `--top 0` (the default) means "show all" — `CheckFileSize.run()` only
  slices `results[:args["top"]]` when `args["top"] > 0`.
- The default `--exclude` list (`Constants.DEFAULT_EXCLUDES`) is applied
  when `--exclude` isn't passed — covered via `FileCollector` constructed
  with `Constants.DEFAULT_EXCLUDES` directly (cheaper than invoking the full
  CLI), asserting a `node_modules`-nested file is skipped by default.

## Files to Change

- `python/tests/check_file_size/test_skip_checks.py` — new, `SkipChecks`
  cases above, plus the two `--top 0` / default-`--exclude` edge cases
  (whichever grouping reads more naturally — same file, since both are
  small and closely related to binary/exclusion detection).
