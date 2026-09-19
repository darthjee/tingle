# Split `_list_pods` tests into their own file

Create `python/tests/kube/test_executor_list_pods.py`, moving the 8 tests
that cover `kube.executor.Kube._list_pods` out of `test_executor.py`:
`test_list_pods_aborts_when_aws_precheck_fails`,
`test_list_pods_prints_namespace_alias_notice_on_pass_through`,
`test_list_pods_prints_inventory_error_on_nonexistent_namespace`,
`test_list_pods_groups_matched_pods_per_alias_in_deterministic_order`,
`test_list_pods_filters_candidates_by_own_namespace_field`,
`test_list_pods_keeps_alias_without_namespace_field_regardless_of_request`
(currently at lines 162-310), plus `test_list_pods_json_output` and
`test_list_pods_prints_discarded_candidates_when_alias_matches_nothing`
(currently near the end of the file, around lines 641-683) — these two are
physically separated from the rest in the current file but test the same
method, so they belong in this new file too.

Give the new file its own module docstring (e.g. `"""Unit tests for
kube.executor.Kube._list_pods."""`), the imports these tests actually use,
and local copies of the `_config` and `_pod` helpers (the small
`MagicMock`-based pod builder). Do not change any test body, assertion, or
mock call.

Do **not** delete these tests from `test_executor.py` yet — cleanup happens
in step 05.

## Files to Change

- `python/tests/kube/test_executor_list_pods.py` — new file with the 8
  `_list_pods` tests (including the JSON-output and discarded-candidates
  ones) and local `_config`/`_pod` helpers.
