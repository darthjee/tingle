# Kubectl inventory helpers

Add a new `kube/inventory.py` module wrapping the two read-only `kubectl` calls this issue needs, following the same non-raising `subprocess.run` pattern as `kube/auth.py` and `kube/scope.py`.

- `list_namespaces() -> tuple[list[dict], str | None]`: runs `kubectl get namespaces -o json`, parses the JSON, returns `(items, None)` on success where `items` is the parsed `"items"` list (each a raw namespace dict), or `([], error)` on a non-zero exit or JSON parse failure.
- `list_pods(namespace: str) -> tuple[list[dict], str | None]`: runs `kubectl get pods -n <namespace> -o json`, same parsing/return shape as above. A `kubectl` error here (e.g. nonexistent namespace) is the source of the "nonexistent namespace → clear error" behavior — surface `error` as-is; callers print it.

Keep these functions dumb wrappers — no alias resolution or filtering here, that's `scope.py` (already) and `matching.py` (next step).

## Files to Change

- `python/kube/inventory.py` — new module: `list_namespaces`, `list_pods`.
- `python/tests/kube/test_inventory.py` — new test file: success and failure (non-zero exit, invalid JSON) cases for both functions, mocking `subprocess.run`.
