# Python Plan: Codacy: subprocess call - check for execution of untrusted input (python/kube/exec.py:27)

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Validate namespace and pod in exec_shell
Import `is_valid_resource_name` from `kube.validation` into `python/kube/exec.py` and, at the top of `exec_shell`, reject an invalid `namespace` (`max_length=63`, matching `inventory.get_pod`'s namespace check) or `pod` (default `max_length=253`) before building the `kubectl` argv, returning `(False, f"invalid namespace: {namespace!r}")` / `(False, f"invalid pod name: {pod!r}")` respectively — mirroring `inventory.get_pod`'s guard exactly. Leave the `# nosec B603, B607` comment on `subprocess.run` as-is (still accurate: fixed binary, list-form args, no shell), and leave `shell` unvalidated (config-sourced, out of scope per the issue).

### Step 2 — Add tests for the new guards
Add `test_exec_shell_invalid_namespace_returns_error` and `test_exec_shell_invalid_pod_returns_error` to `python/tests/kube/test_exec.py`, following the existing test style in that file (`@patch("kube.exec.subprocess.run")`) — assert `success is False`, `error` is not `None`, and `mock_run.assert_not_called()` so the guard short-circuits before any subprocess call, mirroring `inventory.py`'s own validation tests in `python/tests/kube/test_inventory.py`.

## Files to Change
- `python/kube/exec.py` — import `is_valid_resource_name`; validate `namespace`/`pod` in `exec_shell` before building the `kubectl` argv.
- `python/tests/kube/test_exec.py` — add tests covering the invalid-namespace and invalid-pod short-circuits.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- `shell` is intentionally left out of validation — it comes from local config (`Constants.DEFAULT_SHELL` or a user-configured override), not raw external/API input, per the issue's stated scope.
- No change needed to `kube/validation.py` — `is_valid_resource_name` already exists and is reused as-is.
