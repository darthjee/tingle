# Split `_switch` tests into their own file

Create `python/tests/kube/test_executor_switch.py`, moving the 4 tests that
cover `kube.executor.Kube._switch` out of `test_executor.py`
(`test_switch_with_resolved_alias_succeeds`,
`test_switch_with_unresolved_alias_prints_notice_and_passes_through`,
`test_switch_aborts_when_aws_precheck_fails`,
`test_switch_prints_suggestions_on_nonexistent_context` — currently at lines
28-100 of `test_executor.py`, including their `@patch` decorators).

Give the new file its own module docstring (e.g. `"""Unit tests for
kube.executor.Kube._switch."""`), the same `from __future__ import
annotations` and imports these tests actually use (`json` if referenced,
`MagicMock`/`patch` from `unittest.mock`, `Constants`, `Kube`), and a local
copy of the `_config` helper (the small `MagicMock`-based config builder
currently defined at the top of `test_executor.py`) — do not import it from
`test_executor.py`. Do not change any test body, assertion, or mock call.

Do **not** delete `test_executor.py` yet or remove these tests from it —
that happens in step 05, after every group has been extracted, so
`test_executor.py` stays runnable (with temporary duplication) throughout
steps 01-04.

## Files to Change

- `python/tests/kube/test_executor_switch.py` — new file with the 4
  `_switch` tests and a local `_config` helper.
