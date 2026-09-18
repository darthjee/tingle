# Add tests

Add `python/tests/kube/test_validation.py` covering `is_valid_resource_name`: valid names (`"default"`, `"api-abc1234567"`), invalid names (empty string, uppercase, values starting/ending with `-`, values starting with `-` such as `"--kubeconfig=/tmp/evil"`, values over the max length), and the `max_length` boundary itself.

Extend `python/tests/kube/test_inventory.py` (existing patterns already mock `kube.inventory.subprocess.run` and `kube.inventory.binaries.resolve`) with cases for `get_pod` and `list_pods`:
- An invalid `namespace` (e.g. `"--kubeconfig=/tmp/evil"`) returns an error tuple and `subprocess.run` is never called (`mock_run.assert_not_called()`).
- An invalid pod `name` in `get_pod` returns an error tuple and `subprocess.run` is never called.
- Existing success-path tests continue to pass unchanged, since their fixture namespace/pod values (`"default"`, `"nonexistent"`, `"api-abc1234567"`) are already valid RFC 1123 labels.

## Files to Change
- `python/tests/kube/test_validation.py` — new test module for `is_valid_resource_name`.
- `python/tests/kube/test_inventory.py` — add invalid-input cases for `get_pod` and `list_pods`.
