# Issue: Codacy: Method _list_pods has 59 lines of code (limit is 50) (python/kube/executor.py:148)

## Description
Codacy flagged `Kube._list_pods` in `python/kube/executor.py:148` as one of the repository's worst code-quality findings.

- **File**: `python/kube/executor.py:148`
- **Pattern**: `Lizard_nloc-medium` (category: Complexity, severity: Warning)
- **Message**: Method _list_pods has 59 lines of code (limit is 50)
- **Codacy issue ID**: `c6589ca55a38e3a312d15af4db45fb0c`

## Problem
`Kube._list_pods` (python/kube/executor.py:148-214) handles `kube list pods --namespace <alias>` end to end: AWS credential check, resolving the active scope/namespace, fetching pods, filtering aliases for the current namespace, and then building/printing output in two shapes (JSON payload vs. human-readable text), each of which repeats the same per-alias pod-matching and "discarded by id_pattern" lookup logic. The combined length (59 lines) exceeds the project's 50-line Lizard complexity limit.

`Kube._shell` (python/kube/executor.py:216-297) has near-identical per-alias pod-matching and "discarded by id_pattern" lookup logic duplicated from `_list_pods`, even though it wasn't itself flagged by Codacy.

## Expected Behavior
`_list_pods` (and any other methods it delegates to) each stay at or under 50 lines of code, with no change in `kube list pods` behavior or output (JSON or text) for any existing case. `_shell`'s behavior is also unchanged.

## Solution
Extract the per-alias pod matching and the "discarded by id_pattern" lookup into shared static helper method(s) reusable by both `_list_pods` and `_shell`, and extract `_list_pods`'s JSON-payload / text-output building into their own small, well-named static helper methods. Have `_list_pods` and `_shell` call these helpers instead of duplicating the logic inline. Keep the change scoped to `python/kube/executor.py`; no behavior change.

## Benefits
- Resolves the Codacy Lizard_nloc-medium complexity finding.
- Improves readability and testability of the pod-listing/pod-matching logic by separating data fetching/matching from output formatting.
- Removes duplicated pod-matching/discarded-candidate logic between `_list_pods` and `_shell`.
