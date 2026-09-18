# Wire validation into inventory.py

In `python/kube/inventory.py`, import `is_valid_resource_name` from `kube.validation` and call it at the top of `get_pod(namespace, name)` and `list_pods(namespace)`, before the `subprocess.run` call:

- Validate `namespace` with `max_length=63`.
- Validate `name` (in `get_pod`) with the default `max_length=253`.
- On failure, short-circuit with the module's existing error-tuple contract: `([], f"invalid namespace: {namespace!r}")` for `list_pods`, and `(None, f"invalid namespace: {namespace!r}")` / `(None, f"invalid pod name: {name!r}")` for `get_pod` — never raise, matching the module docstring's contract.

Leave `list_namespaces()` untouched (no caller-supplied input) and leave the existing `# nosec B603, B607` comments on all three `subprocess.run` calls in place — they still correctly document why shell injection and partial-path resolution are not concerns here; the new validation addresses the separate argument-injection angle.

## Files to Change
- `python/kube/inventory.py` — add validation calls and early-return error paths in `get_pod` and `list_pods`.
