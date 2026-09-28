# Wire the flags into executor.py
- Add `--ignore` and `--include` to `FLAGS`, after `--exclude` and before
  `--ext`: `type: str`, `action: "append"`, `default: None`, using the help
  texts from the shared contracts.
- In `CheckFileSize.run`, build the collector as
  `FileCollector(excludes, args["ext"], ignore=args["ignore"] or [], include=args["include"] or [])`.
- Add examples to the module docstring:
  - `./check_file_size.py . --ignore '*.test.js' --ignore 'docs/**'`
  - `./check_file_size.py . --include 'src/**' --ext .py`

Tests to add in `python/tests/check_file_size/test_executor.py`:
- both flags parse as repeatable lists and reach the collector (end-to-end with
  `tmp_path` files, checking which paths appear in the output);
- when every file is filtered out, the run prints "No files found for
  analysis." and exits 0.

## Files to Change
- `python/check_file_size/executor.py` — the two new `FLAGS` entries, the collector call and the docstring examples.
- `python/tests/check_file_size/test_executor.py` — new cases.
