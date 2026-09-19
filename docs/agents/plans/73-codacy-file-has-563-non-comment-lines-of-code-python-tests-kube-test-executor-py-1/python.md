# Python Plan: Codacy: File has 563 non-comment lines of code (python/tests/kube/test_executor.py:1)

Main plan: [plan.md](plan.md)

## Steps

- [01 — Split `_switch` tests into their own file](python/01-split-switch-tests.md)
- [02 — Split `_list_namespace` tests into their own file](python/02-split-list-namespace-tests.md)
- [03 — Split `_list_pods` tests into their own file](python/03-split-list-pods-tests.md)
- [04 — Split `_shell` tests into their own file](python/04-split-shell-tests.md)
- [05 — Split `_configure`/`run` tests and remove the original file](python/05-split-dispatch-tests-and-cleanup.md)

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`, includes coverage via `--cov-fail-under=75`)

## Notes

- `python/tests/kube/` has no `conftest.py` anywhere today, and existing
  multi-file test setups in this directory (e.g. `test_configure.py`) already
  define their own small local fixture-builder helpers rather than sharing
  one. Follow that existing convention: duplicate the tiny `_config`
  (and `_pod`, where needed) helper functions into each new file below,
  rather than introducing this directory's first `conftest.py`. This departs
  from the issue's suggested `conftest.py` approach, which the issue text
  explicitly left as an implementation detail for planning.
- Each new file stays well under the `check_file_size` warn threshold (300
  lines) based on current line spans, so there is no risk of just moving the
  problem into a differently-shaped oversized file.
- `kube.executor.Kube._configure` and `run` are covered together in step 05
  since they're both small (4 tests total) and neither warrants its own file.
- Do not confuse `test_executor_dispatch.py` (tests the `_configure` dispatch
  method on `Kube`) with the existing `test_configure.py` (tests the
  `kube.configure` module's `configure_context`/`configure_namespace`/
  `configure_pod` functions) — they test different things and both must keep
  existing.
