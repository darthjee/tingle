# Split `_list_namespace` tests into their own file

Create `python/tests/kube/test_executor_list_namespace.py`, moving the 4
tests that cover `kube.executor.Kube._list_namespace` out of
`test_executor.py`: `test_list_namespace_aborts_when_aws_precheck_fails`,
`test_list_namespace_prints_alias_arrow_name_and_bare_name`,
`test_list_namespace_prints_inventory_error` (currently at lines 103-159),
plus `test_list_namespace_json_output` (currently near the end of the file,
around line 618) — this last one is physically separated from the other
three in the current file but tests the same method, so it belongs in this
new file too.

Give the new file its own module docstring (e.g. `"""Unit tests for
kube.executor.Kube._list_namespace."""`), the imports these tests actually
use, and a local copy of the `_config` helper. Do not change any test body,
assertion, or mock call.

Do **not** delete these tests from `test_executor.py` yet — cleanup happens
in step 05.

## Files to Change

- `python/tests/kube/test_executor_list_namespace.py` — new file with the 4
  `_list_namespace` tests (including the JSON-output one) and a local
  `_config` helper.
