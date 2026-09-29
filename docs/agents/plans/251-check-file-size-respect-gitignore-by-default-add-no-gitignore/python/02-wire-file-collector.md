# Wire gitignore into FileCollector
In `python/check_file_size/file_collector.py`:

- add a keyword-only `gitignore: bool = True` to `__init__` and document it
  in the docstring;
- in `collect()`, when `gitignore` is on, call `GitIgnore.ignored_paths` once:
  with the (resolved) target for a directory, with its parent for a single
  file. Treat `None` as "nothing ignored";
- directory walk: apply the check after `_is_excluded` and before the glob
  filters (`_accepts`), i.e. step 3 of the pipeline;
- single file: skip it when the ignored set contains it, before `_accepts`.

Keep the method small (Codacy cyclomatic-complexity limit is 10): e.g. a
`_git_ignored(root)` helper returning the `GitIgnored` or `None`, and an
`_is_git_ignored(ignored, path)` check.

Extend `python/tests/check_file_size/test_file_collector.py` (mock
`GitIgnore.ignored_paths` with `monkeypatch`):
- ignored files (both a file entry and a file under a directory prefix) are
  dropped when enabled;
- the same files are kept with `gitignore=False`, and the helper is not called;
- `None` from the helper drops nothing;
- a single-file target that is ignored returns `[]`, and the helper is called
  with the file's parent;
- the helper is called once per `collect()`, not per file.

## Files to Change
- `python/check_file_size/file_collector.py` — `gitignore` option and filter step 3.
- `python/tests/check_file_size/test_file_collector.py` — gitignore cases.
