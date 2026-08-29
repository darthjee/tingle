# Pod-matching pipeline

Add a new `kube/matching.py` module implementing the reusable prefix + `id_pattern` + deterministic-ordering pipeline described in the issue (steps 3–6 of its "Solution" section; steps 1–2, active-scope detection and namespace-alias resolution, are already covered by `kube/scope.py`). This is the piece child #4's `shell` will call into directly rather than re-implementing.

- `match_pods(pods: list[dict], prefix: str, id_pattern: str | None, default_id_pattern: str) -> list[dict]`:
  1. Filter `pods` to those whose name starts with `prefix`.
  2. For each remaining pod, take the part of the name after `prefix` and match it against `id_pattern` (or `default_id_pattern` when `id_pattern` is falsy/`None`) via `re.fullmatch`; discard non-matches. This is what excludes e.g. `my-pod-super-<id>` from a `myp`-prefixed alias whose `id_pattern` doesn't allow the `-super-` segment.
  3. Sort the surviving pods by `creationTimestamp` ascending (oldest first) — deterministic ordering, never a collapse to one.
  4. Return the ordered list (pod dicts, as received from `kube/inventory.py`).
- Accept pod dicts shaped like `kubectl get pods -o json` items (`metadata.name`, `metadata.creationTimestamp`) — extract via `pod["metadata"]["name"]` / `pod["metadata"]["creationTimestamp"]`, no reshaping.

## Files to Change

- `python/kube/matching.py` — new module: `match_pods`.
- `python/tests/kube/test_matching.py` — new test file: prefix filter, `id_pattern` false-positive exclusion (the `my-pod-super-<id>` vs. `myp` case from the parent issue), fallback to `default_id_pattern` when a pod alias has none, and ordering by `creationTimestamp` when multiple candidates remain.
