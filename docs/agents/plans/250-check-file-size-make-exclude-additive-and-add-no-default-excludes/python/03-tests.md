# Tests

Add or adjust tests under `python/tests/check_file_size/`.

`test_executor.py`:
- `_resolve_excludes`: no flags → `DEFAULT_EXCLUDES`; `exclude="x"` → defaults + `x`;
  `no_default_excludes=True` → `[]`; both → `["x"]`; `" x, ,y"` → blanks dropped;
  `exclude="dist"` → no duplicate; `exclude=""` / `","` → defaults only.
- End-to-end via `run` (reuse the `FileCollector.__init__` spy pattern of
  `test_run_passes_glob_lists_to_collector`): `--exclude fixtures` still skips a
  `node_modules/` file *and* a `fixtures/` file; `--no-default-excludes` analyses a
  file under `node_modules/`.
- Update any existing test that relied on `--exclude` replacing the defaults.

`test_file_collector.py`:
- A target directory whose own path contains an exclude name (e.g.
  `tmp_path / "build" / "proj"` with `excludes=["build"]`) still collects the files
  below it.
- Whole-component match: `build` excludes `build/x.js` and `a/build/y.js`, not
  `builder/z.js`.
- Case-insensitive match (`Build/x.js` with `build`) — extend the existing
  `test_collect_excludes_directory_component_case_insensitive` if it already covers it.
- A single-file target inside an excluded-name directory is still returned.

## Files to Change
- `python/tests/check_file_size/test_executor.py` — new and updated tests.
- `python/tests/check_file_size/test_file_collector.py` — new tests.
