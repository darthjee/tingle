# Add/update test coverage

Two existing tests in `test_config.py` assert the old missing-file behavior and must be rewritten for the bootstrap; new tests cover the bootstrap itself and the end-to-end `configure context` first-run path.

In `python/tests/kube/test_config.py`:
- Replace `test_missing_config_file_falls_back_to_pass_through` with a test asserting the new bootstrap behavior: `KubeConfig(missing)` sets `pass_through is False`, `notice` mentions "created" and the path, `data["version"] == Constants.CURRENT_VERSION`, and the file now exists on disk containing `{"version": Constants.CURRENT_VERSION}`.
- Replace `test_raw_is_empty_when_file_missing` with `test_raw_is_bootstrapped_when_file_missing`, asserting `config.raw == {"version": Constants.CURRENT_VERSION}`.
- Add a test that a second `KubeConfig(same_path)` instantiation, after the first bootstrapped it, loads normally (`pass_through is False`, `notice is None`) — confirming no re-bootstrap/duplicate notice on subsequent reads.
- Leave `test_invalid_json_falls_back_to_pass_through`, `test_non_object_config_falls_back_to_pass_through`, `test_missing_required_key_falls_back_to_pass_through`, `test_object_key_with_wrong_type_falls_back_to_pass_through`, and `test_pod_entry_missing_prefix_falls_back_to_pass_through` unchanged — they cover a *present-but-broken* file, which must still fall back to pass-through untouched by this fix.

In `python/tests/kube/test_configure.py`:
- Add an end-to-end test that calls `configure_context` (or drives `Kube().run(["configure", "context"])`, matching the file's existing invocation style) against a `tmp_path` config file that does not exist yet, feeding `input()` the `create` action plus an alias/ARN pair. Assert the run succeeds with no "config missing required key(s): version" message, and that the resulting file on disk contains both the bootstrapped `version` key and the new `contexts` alias.

In `python/tests/kube/test_executor.py` (if it covers `Kube.run()`'s notice-printing branch — check for an existing test around `config.pass_through`/`config.notice` printing): add/adjust a test asserting the notice is printed when `notice` is set but `pass_through` is `False`, matching the Step 2 change.

Run `pytest` and `ruff check .` from `python/` locally to confirm everything passes before this step is considered done.

## Files to Change

- `python/tests/kube/test_config.py` — replace the two missing-file assertions, add the re-read/no-duplicate-notice test.
- `python/tests/kube/test_configure.py` — add the first-run bootstrap end-to-end test.
- `python/tests/kube/test_executor.py` — add/adjust the notice-printing test if this file exists and covers that branch.
