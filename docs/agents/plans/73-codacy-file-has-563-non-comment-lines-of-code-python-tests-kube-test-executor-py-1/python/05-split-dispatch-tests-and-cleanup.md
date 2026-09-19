# Split `_configure`/`run` tests and remove the original file

Create `python/tests/kube/test_executor_dispatch.py`, moving the 4 remaining
tests out of `test_executor.py`: `test_configure_dispatches_to_configure_context`,
`test_configure_dispatches_to_configure_namespace`,
`test_configure_dispatches_to_configure_pod` (covering
`kube.executor.Kube._configure`'s dispatch logic — not to be confused with
`python/tests/kube/test_configure.py`, which tests the `kube.configure`
module's own functions), and `test_run_prints_notice_when_set_without_pass_through`
(covering `Kube.run`) — currently at lines 552-618.

Give the new file its own module docstring (e.g. `"""Unit tests for
kube.executor.Kube._configure dispatch and Kube.run."""`), the imports these
tests actually use, and a local copy of the `_config` helper if any of them
need it. Do not change any test body, assertion, or mock call.

Once all 28 tests have been moved across steps 01-05 (4 `_switch` + 4
`_list_namespace` + 8 `_list_pods` + 8 `_shell` + 4 dispatch/run = 28),
delete `python/tests/kube/test_executor.py` entirely — nothing should remain
in it.

Finally, run `pytest` from `python/` and confirm:
- All tests that previously lived in `test_executor.py` still pass, now
  spread across the 5 new files, with the same total test count (28).
- Coverage for `kube/executor.py` is unaffected (the `--cov-fail-under=75`
  gate in `python/pyproject.toml` still passes).
- `ruff check .` from `python/` is clean on the new files.

## Files to Change

- `python/tests/kube/test_executor_dispatch.py` — new file with the 3
  `_configure`-dispatch tests and the 1 `run` test.
- `python/tests/kube/test_executor.py` — delete (now empty of tests).
