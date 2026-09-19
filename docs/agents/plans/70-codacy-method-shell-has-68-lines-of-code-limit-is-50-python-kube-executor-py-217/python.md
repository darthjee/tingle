# python Plan: Codacy: Method _shell has 68 lines of code (limit is 50) (python/kube/executor.py:217)

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Extract pod-alias resolution into a helper method
In `python/kube/executor.py`, pull the block of `Kube._shell` that decides the real pod name out into a new `@staticmethod` helper (e.g. `_resolve_real_pod(parsed, real_namespace, active_scope, config)`), covering exactly:

- the "pod alias not configured — use it as-is" fallback (with its notice print), including the namespace-mismatch warning print for a configured alias whose `namespace` differs from `parsed["namespace_alias"]`
- fetching pods via `list_pods(real_namespace)` and printing/handling its error
- matching via `Kube._match_pods_for_alias`, printing the "no pods matched" message plus discarded candidates when nothing matches
- resolving to a single real pod name when exactly one match, or prompting via `prompt_pod_choice` when multiple match, including the "no pod selected" message

Have the helper return the resolved real pod name (`str`) on success, or `None` when resolution failed — in every `None` case the helper itself must already have printed the same message `_shell` prints today, so behavior is byte-for-byte identical. Do not change any print wording or ordering.

### Step 2 — Refactor `_shell` to use the new helper
Update `Kube._shell` to call the new helper right after resolving `real_namespace`, and `return` immediately when it gets back `None`. The rest of `_shell` (fetching the pod via `get_pod`, the running-phase warning, and `exec_shell`) stays as-is. Confirm the resulting `_shell` and the new helper are each comfortably under 50 lines.

## Files to Change
- `python/kube/executor.py` — extract the pod-resolution block of `_shell` into a new static helper method; `_shell` becomes a short orchestrator calling it.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- `python/tests/kube/test_executor.py` already tests `_shell` end-to-end (single match, multiple matches with prompt, zero matches, pass-through alias, namespace-mismatch warning, non-running pod, `list_pods`/`get_pod` errors) by calling `Kube._shell(...)` directly and asserting on printed output — none of these assertions should need to change if the extraction preserves exact behavior and message text. Run the full suite (`pytest`) to confirm before considering this done.
- This mirrors the same extraction pattern already used for `_list_pods` in issue #62 (PR #96), where `_pods_json_payload`/`_print_pods_text` were split out and `_match_pods_for_alias` was introduced as a shared helper `_shell` already calls today.
- No new unit tests are required for the new helper itself, consistent with how `_match_pods_for_alias` (from issue #62) has no dedicated test — it's exercised indirectly through `_shell`'s and `_list_pods`'s existing tests.
