# Examples Plan: kube list pods: option to list all pods found in the server

Main plan: [plan.md](plan.md)

## Shared contracts

- Command: `tingle kube list pods --namespace shop --all`.
- Output: alias blocks, then an always-printed `(unmatched):` block of pods
  matched by no alias (oldest first). Sample:

  ```
  api:
    - shop-api-5f7c9d8b6a-k3m8p
    - shop-api-5f7c9d8b6a-q7n2w
  (unmatched):
    - shop-redis-0
    - shop-migrate-28391740-x8k2l
  ```

## Implementation Steps

### Step 1 — Add a "List all pods" step to the kube walkthrough

In `examples/kube/end_to_end.txt`, insert a new step right after "6. List
pods": title "List all pods", purpose "also list the pods in namespace shop
that no pod alias matches", the command and the sample output above, plus a
one-line note that `--all` covers only the given namespace. Renumber the
following steps (current 7 onward) and any references to them.

## Files to Change

- `examples/kube/end_to_end.txt` — new step and renumbering.

## CI Checks

- `python/`: `pytest tests/kube/test_example.py` (the file must stay ASCII
  only).

## Notes

- Keep the walkthrough's existing formatting (title underline length, two-space
  indentation).
