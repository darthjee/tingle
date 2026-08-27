# Unit tests: FileCollector

Cover `python/check_file_size/file_collector.py`'s `FileCollector.collect()`
and `_is_excluded()`, using `tmp_path` (pytest's built-in fixture) to build
real small file trees rather than mocking the filesystem.

Cases:
- `collect()` on a single file path (not a directory): returns `[path]` if
  not binary, `[]` if `SkipChecks.is_binary_file` says binary.
- `collect()` on a directory: recurses (`rglob("*")`), returns only files
  (skips subdirectories themselves).
- `--exclude` behavior: any path component matching an exclude entry
  (case-insensitive, per `_is_excluded`'s `.lower()`) is skipped, e.g. a
  file inside a `node_modules/` subfolder.
- `--ext` filter: only files whose suffix (case-insensitive) is in the
  extension set are kept; `None` extension filter (not passed) means no
  filtering by extension.
- Binary files (by extension or content, via `SkipChecks`) are excluded from
  directory collection the same way as the single-file case.
- Empty directory → `[]`.
- Non-existent path → `[]` (`target.is_file()` and `target.is_dir()` both
  false).
- Permission-denied directory: a subdirectory `chmod`'d to deny read/execute
  access is skipped without raising (only meaningful when the test process
  is non-root — see `python/Dockerfile`'s non-root user, step 03).

## Files to Change

- `python/tests/check_file_size/__init__.py` — new, empty (package marker).
- `python/tests/check_file_size/test_file_collector.py` — new, cases above.
