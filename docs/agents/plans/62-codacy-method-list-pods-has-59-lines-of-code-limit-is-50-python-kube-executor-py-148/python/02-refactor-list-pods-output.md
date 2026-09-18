# Refactor _list_pods to use the shared helper and split output building

Rewrite `Kube._list_pods` to:
1. Keep the existing AWS pre-check, active-scope detection, namespace resolution, `list_pods(...)` call, and alias filtering as-is (these are the parts that make it 59 lines when combined with output building).
2. Call the new `_match_pods_for_alias` helper (from step 01) instead of inlining `match_pods(...)` + discarded computation, for both the JSON and text branches.
3. Extract JSON payload construction into a new static helper, e.g. `_pods_json_payload(pods, items, default_id_pattern)`, returning the same list-of-dicts shape currently built inline (`{"alias": ..., "pods": [...]}`).
4. Extract text output printing into a new static helper, e.g. `_print_pods_text(pods, items, default_id_pattern)`, preserving the exact current print format: `"{alias}:"`, `"  - {pod_name}"` per matched pod, and the `"  kube list: candidates discarded by id_pattern for '{alias}':"` block with `"    - {name}"` lines when nothing matched but candidates were discarded.

After this step, `_list_pods` itself should read as: pre-check → scope/namespace resolution → fetch pods → filter aliases → dispatch to `_pods_json_payload` (when `parsed.get("json")`) or `_print_pods_text` otherwise. No change to printed output, JSON shape, or `list_pods`/`match_pods` call arguments — existing tests in `python/tests/kube/test_executor.py` (`test_list_pods_*`) must keep passing unmodified.

## Files to Change
- `python/kube/executor.py` — rewrite `_list_pods` and add `_pods_json_payload` / `_print_pods_text` static helpers, both using `_match_pods_for_alias` from step 01.
