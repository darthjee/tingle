# Print unmatched pods in list pods

Teach `Kube._list_pods` to honor `parsed.get("all")`:

- Match each displayed alias once (reuse `_match_pods_for_alias`) and collect
  the names of every matched pod. Unmatched pods are the `items` whose name is
  not in that set, sorted by `metadata.creationTimestamp` ascending (same key
  as `match_pods`). Prefer a small helper (e.g. `_unmatched_pods(items,
  matched_names)`) and avoid matching each alias twice.
- `_pods_json_payload`: when `--all`, append `{"alias": None, "pods": [names]}`
  as the last entry (always, even if empty).
- `_print_pods_text`: when `--all`, skip the "candidates discarded by
  id_pattern" hint, and after the alias blocks print `(unmatched):` followed by
  `  - <name>` per unmatched pod (header always printed).
- Without `--all`, behavior and output are unchanged.

Edge cases to cover: no active scope / no pod aliases (only the `(unmatched)`
group, containing every pod); empty namespace (empty alias blocks and an empty
`(unmatched):`); kubectl error or failed AWS pre-check (unchanged: error
printed, nothing listed); a pod matched by two aliases (listed under both,
not unmatched); aliases filtered out by `namespace` don't count as matches.

## Files to Change

- `python/kube/executor.py` — `_list_pods`, `_pods_json_payload`,
  `_print_pods_text`, plus the unmatched helper.
- `python/tests/kube/test_executor_list_pods.py` — tests for text and JSON
  with `--all` (mixed matched/unmatched, ordering by creation time, no active
  scope, empty namespace, overlapping aliases, discarded hint suppressed,
  namespace-filtered alias pods land in unmatched), plus a regression test
  that output without `--all` is unchanged.
