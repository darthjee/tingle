# Python Plan: Codacy: Method _shell has a cyclomatic complexity of 17 (limit is 10) (python/kube/executor.py:217)

Main plan: [plan.md](plan.md)

## Overview
Codacy reported `Lizard_ccn-minor` for `_shell` in `python/kube/executor.py:217` (CCN 17, limit 10). That location is from before #70 (commit 77f2e6c), which moved the pod-resolution logic into `_resolve_real_pod`. Lizard on current `main` shows `_shell` (line 300) at CCN 7 and `_resolve_real_pod` (line 241) at CCN 10, with no function over the limit.

## Context
- `_resolve_real_pod` is exactly at the limit (10). The Codacy rule flags only values above 10, so it passes, but any further branch added to it would trip the finding.
- Existing tests in `python/tests/kube/test_executor_shell.py` cover the `kube shell` flow.

## Implementation Steps

### Step 1 — Re-verify complexity on the branch
Run Lizard against `python/kube/executor.py` with a CCN limit of 10 (for example `pip install lizard && lizard -C 10 python/kube/executor.py`). Confirm that no function exceeds the limit and that `_shell` is at or below 10. If a function does exceed it, extract the offending branch into a small private static method on `Kube`, keeping `kube shell` behavior and output unchanged, and follow the existing static-method style in the file.

### Step 2 — Run the Python checks
Run `ruff check .` and `pytest` from `python/` to confirm nothing regressed. No source change is expected, so if Step 1 needed no edit the branch will hold only the issue and plan docs. In that case, report that the finding is already resolved by #70 so the issue can be closed once Codacy re-analyzes.

## Files to Change
- `python/kube/executor.py` — only if Step 1 finds a function over CCN 10; otherwise unchanged.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- The expected outcome is no code change. The Codacy finding should clear on its next analysis of `main`.
- Splitting `_resolve_real_pod` for headroom below 10 was left out on purpose. It would be an optional refactor beyond what this issue asks.
