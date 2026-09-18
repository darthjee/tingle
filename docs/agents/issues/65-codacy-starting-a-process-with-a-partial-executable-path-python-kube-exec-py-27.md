# Issue: Codacy: Starting a process with a partial executable path (python/kube/exec.py:27)

## Description
Codacy flagged `python/kube/exec.py:27` as a partial-executable-path warning (Bandit `B607`), one of the repository's worst code-quality findings.

## Problem
The finding is stale. `exec_shell`'s `subprocess.run` call already resolves `kubectl` via `binaries.resolve("kubectl")` (added in #58/PR #78) and carries a `nosec B603, B607` annotation, matching the same already-fixed pattern documented for `inventory.py` in issue #59.

## Expected Behavior
Codacy's dashboard should reflect that this call site is already resolved; no behavior change is expected in `exec.py`.

## Solution
Same as #59: add a short comment at the `exec_shell` call site noting that B607 is already resolved via `binaries.resolve()`, for future Codacy re-scans and readers. No functional change.

## Benefits
Keeps the code-quality trail consistent with the same finding already resolved elsewhere in `python/kube`, and gives future re-scans/readers explicit context instead of re-surfacing a stale warning.
