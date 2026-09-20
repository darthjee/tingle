# Issue: Codacy: Starting a process with a partial executable path (python/kube/scope.py:46)

## Description
Codacy flagged `python/kube/scope.py:46` for `Bandit_B607` ("Starting a process with a partial executable path"). At the time of the scan, that line was the `subprocess.run(["kubectl", "config", "current-context"], ...)` call inside `switch_context`.

## Problem
Investigation shows this finding was already resolved before this issue was even opened:

- Commit `87b9f76` (PR #78, "Fix #58 — Codacy: partial executable path in python/kube") merged at 2026-09-15 17:38 UTC.
- That fix added `python/kube/binaries.py` (a `shutil.which`-based resolver) and applied `binaries.resolve()` to every `subprocess.run` call site in `scope.py`, including the `kubectl config current-context` call that sat on line 46.
- This issue (#61) was created at 2026-09-15 15:54:32 UTC, over an hour *before* that fix merged, so the Codacy scan behind it ran against the pre-fix code.
- The current `python/kube/scope.py` already resolves every subprocess binary via `binaries.resolve(...)` and carries `# nosec B603, B607` justification comments at each call site. Line 46 today is no longer a subprocess call at all.
- The sibling issue #68 (`scope.py:36`, same pattern, created 10 seconds later) was closed as already fixed for the same reason.

## Solution
No code change needed — the flagged pattern no longer exists in `scope.py`. Close this issue as already fixed (superseded by #58 / PR #78). A fresh Codacy re-scan should stop reporting this finding.

## Benefits
Keeps the issue tracker accurate and avoids redundant work re-fixing something already fixed.
