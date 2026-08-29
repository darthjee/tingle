# Add single-pod fetch helper

`kube/inventory.py` currently only has `list_pods(namespace)` (whole-namespace listing). The `shell` command's Running-phase pre-check needs a single-pod fetch: `kubectl get pod -n <ns> <pod> -o json`. Add a `get_pod(namespace, name)` function following the exact same shape/conventions as `list_namespaces`/`list_pods` (dumb `subprocess.run` wrapper, no alias resolution, never raises).

Returns a `(pod, error)` tuple: `pod` is the parsed JSON object (or `None`), `error` is `None` on success or a message on non-zero exit / JSON parse failure (e.g. nonexistent pod name).

## Files to Change

- `python/kube/inventory.py` — add `get_pod(namespace: str, name: str) -> tuple[dict | None, str | None]`.
- `python/tests/kube/test_inventory.py` — add coverage for `get_pod`: success (parses the single object from `kubectl get pod ... -o json`), non-zero exit (nonexistent pod), and JSON parse failure, matching the existing `list_pods` test style.
