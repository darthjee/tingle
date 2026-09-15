# Update tests for the new resolution behavior

Add unit tests for the new `kube/binaries.py` helper, and update every existing test that asserts the exact `subprocess.run` argument list in `test_auth.py`, `test_exec.py`, `test_inventory.py`, and `test_scope.py` to account for `binaries.resolve(...)` running first. Mock `kube.<module>.binaries.resolve` (or `shutil.which` directly) to return a deterministic value (e.g. the bare name itself, or a fixed fake path) so assertions stay stable regardless of what's actually on the test runner's `PATH`.

## Files to Change
- `python/tests/kube/test_binaries.py` — new test module: covers `resolve` returning the `shutil.which` result when found, and falling back to the bare name when `shutil.which` returns `None`.
- `python/tests/kube/test_auth.py` — patch `kube.auth.binaries.resolve` (or `shutil.which`) in each test; update `test_passes_correct_profile_through`'s `assert_called_once_with` to expect the resolved/mocked value instead of the bare `"aws"`.
- `python/tests/kube/test_exec.py` — same pattern for `kube.exec.binaries.resolve`/`kubectl`.
- `python/tests/kube/test_inventory.py` — same pattern for `kube.inventory.binaries.resolve`/`kubectl`, across `list_namespaces`, `get_pod`, and `list_pods` tests.
- `python/tests/kube/test_scope.py` — same pattern for `kube.scope.binaries.resolve`, covering both `kubectx` and `kubectl` call sites.
