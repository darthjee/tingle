# Add --no-gitignore to the executor and help
In `python/check_file_size/executor.py`:
- add the `--no-gitignore` entry to `FLAGS` right after
  `--no-default-excludes` (see Shared contracts for the exact dict);
- pass `gitignore=not args["no_gitignore"]` to `FileCollector` in `run()`;
- add `./check_file_size.py . --no-gitignore` to the module docstring
  examples, and mention in the docstring that git-ignored files are skipped
  by default.

In `commands/python.json`, `check_file_size.long_help`, "File selection"
section: add a `--no-gitignore` entry after `--no-default-excludes` stating
that, by default, untracked files ignored by git (`.gitignore`,
`.git/info/exclude`, global excludes) are skipped when `<path>` is in a git
repository, tracked files are always analysed, and nothing is skipped
without git; add `./check_file_size.py . --no-gitignore` to Examples. Keep
the file valid JSON and the column alignment of the existing text.

Extend `python/tests/check_file_size/test_executor.py`:
- `--no-gitignore` reaches the collector as `gitignore=False`, and its
  absence as `gitignore=True` (spy on `FileCollector.__init__` or
  monkeypatch the class, following the existing style);
- an end-to-end run in a temporary git repo (skipped without git) shows an
  ignored untracked file is absent from the report by default and present
  with `--no-gitignore`.

## Files to Change
- `python/check_file_size/executor.py` — flag, wiring, docstring.
- `commands/python.json` — `long_help` for `--no-gitignore`.
- `python/tests/check_file_size/test_executor.py` — flag wiring tests.
