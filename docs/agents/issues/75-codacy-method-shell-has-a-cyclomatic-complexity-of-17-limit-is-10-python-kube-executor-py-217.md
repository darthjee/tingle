# Issue: Codacy: Method _shell has a cyclomatic complexity of 17 (limit is 10) (python/kube/executor.py:217)

## Description
Codacy flagged `Kube._shell` in `python/kube/executor.py:217` for a cyclomatic complexity of 17 (limit is 10).

- **Pattern**: `Lizard_ccn-minor` (category: Complexity, severity: Info)
- **Codacy issue ID**: `b6d38ae9763943a55a5dd8e507b11ea2`

## Problem
The finding was reported against `_shell` as it was before #70 (commit 77f2e6c, 2026-09-19), when it held the pod-resolution logic inline (68 lines). That refactor extracted `_resolve_real_pod`, so the finding is likely stale.

## Expected Behavior
No method in `python/kube/executor.py` exceeds a cyclomatic complexity of 10, and `kube shell` behavior is unchanged.

## Solution
Measured with Lizard on the current `main`: `_shell` (line 300) has CCN 7 and `_resolve_real_pod` (line 241) has CCN 10; no function exceeds the limit. If Codacy still reports the finding after re-analysis, no code change is needed and the issue can be closed. Optionally, `_resolve_real_pod` sits exactly at the limit and could be split further.
