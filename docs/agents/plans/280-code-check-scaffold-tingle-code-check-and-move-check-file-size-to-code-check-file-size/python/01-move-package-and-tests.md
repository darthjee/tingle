# Move the package and tests
Create `python/code_check/__init__.py` and `python/code_check/file_size/__init__.py`, each holding only a docstring.
Use `git mv` to move every module except `__init__.py` and `main.py` from `python/check_file_size/` to
`python/code_check/file_size/`. That is `executor.py`, `config.py`, `constants.py`, `palette.py`, `reporter.py`,
`file_analyzer.py`, `file_collector.py`, `git_ignore.py`, `glob_matcher.py` and `skip_checks.py`. Keep
`executor.py` at mode 100755. `palette.py` moves up again in step 02; moving it here first keeps the history simple.

Rewrite every absolute `check_file_size.` import to `code_check.file_size.`. Fix the `sys.path.insert` in
`executor.py` (L52): at the new depth, `parent.parent` resolves to `python/code_check`, so use `parents[2]`
(→ `python/`) or drop it if nothing needs it. Existing relative imports inside the package stay valid.

Tests: `git mv` every file in `python/tests/check_file_size/` except `test_main.py` to
`python/tests/code_check/file_size/`. That includes `conftest.py` and the `test_*` modules. Add `__init__.py` files
where the test tree needs them. Update the imports and monkeypatch targets, e.g.
`test_git_ignore.py:12` (`from code_check.file_size import git_ignore`). `test_main.py` stays in
`python/tests/check_file_size/`. It keeps testing `check_file_size/main.py` (still patching `CheckFileSize` on that
module) and is finalised as the shim test in step 06. Copy the autouse `_isolate_home` fixture into a
`python/tests/code_check/conftest.py` (or keep one at `tests/code_check/`), so the new dispatcher and config tests
get it too. `python/tests/check_file_size/` keeps its `__init__.py` and `conftest.py` for the shim test.

In `python/pyproject.toml`, add `code_check` to the coverage `source` and keep `check_file_size`, giving
`["check_file_size", "code_check", "common", "kube"]`.

After this step, `ruff check . && pytest` must pass. At this point `python/check_file_size/main.py` imports from
`code_check.file_size.executor`, as a temporary state until step 06.

## Files to Change
- `python/code_check/__init__.py`, `python/code_check/file_size/__init__.py` — new packages.
- `python/check_file_size/*.py` → `python/code_check/file_size/*.py` — `git mv`, then fix the imports and the `sys.path` depth.
- `python/check_file_size/main.py` — point the import at `code_check.file_size.executor`.
- `python/tests/check_file_size/*` → `python/tests/code_check/file_size/*` — `git mv`, then fix the imports and patch targets.
- `python/tests/code_check/conftest.py` — HOME isolation for the whole `code_check` test tree.
- `python/pyproject.toml` — add `code_check` to the coverage `source`.
