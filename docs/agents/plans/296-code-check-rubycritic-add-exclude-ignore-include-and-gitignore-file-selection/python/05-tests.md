# Tests

Cover, under `python/tests/code_check/rubycritic/`:

- each flag: `--exclude` (merge, blanks, dedup, last wins), `--no-default-excludes`,
  `--ignore`, `--include` (combined with `.rb`), gitignore on/off (fake git
  fixture modelled on `file_size`'s `fake_git`); replace
  `test_directory_gitignore_is_not_applied`;
- filter order: a file matched by several steps is dropped by the first;
- single-file `<path>`: excludes do not apply, globs match the file name;
- symlinks: relative inside (reported as target, deduped), outside (skipped),
  absolute inside (kept as target's relative path), dangling (skipped),
  directory symlink not walked;
- a non-UTF-8 `.rb` file is kept;
- executor end-to-end: `--exclude`/`--ignore` reflected in stdin lines, and a
  symlink's stdin line is its target; autouse stub for `GitIgnore.ignored_paths`;
  update `test_select_warns_about_unsendable_names`'s `select_files` fake to accept
  the new keyword arguments.

Also: `outside_symlinks` default/False cases for `FileCollector`; tests for the
new excludes helper; update `test_flags.py` (flag order, defaults dict, help
texts, append/store behaviour) and `python/tests/code_check/test_completion.py`
(rubycritic flag names, free-value flags; keep the `--ext`/`--no-config` absence test).
`file_size`'s existing tests must pass unchanged.

## Files to Change
- `python/tests/code_check/rubycritic/test_selection.py`
- `python/tests/code_check/rubycritic/test_executor.py`
- `python/tests/code_check/rubycritic/test_flags.py`
- `python/tests/code_check/test_completion.py`
- `python/tests/code_check/file_size/test_file_collector.py` — new `outside_symlinks` cases only.
- `python/tests/code_check/test_excludes.py` — new.
