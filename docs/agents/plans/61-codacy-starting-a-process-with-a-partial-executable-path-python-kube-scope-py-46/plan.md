# Plan: Codacy: Starting a process with a partial executable path (python/kube/scope.py:46)

Issue: [61-codacy-starting-a-process-with-a-partial-executable-path-python-kube-scope-py-46.md](../../issues/61-codacy-starting-a-process-with-a-partial-executable-path-python-kube-scope-py-46.md)

## Overview
Codacy's `Bandit_B607` finding on `python/kube/scope.py:46` is stale: it was raised against code that predates fix #58 (PR #78). No source change is required. This plan confirms the current state of `scope.py` and closes the issue as already fixed.

## Context
- The finding was reported against the `subprocess.run(["kubectl", "config", "current-context"], ...)` call in `switch_context`, which sat on line 46 before commit `87b9f76`.
- Commit `87b9f76` (PR #78) added `python/kube/binaries.py` (`shutil.which`-based resolver) and routed every `subprocess.run` call in `scope.py` through `binaries.resolve(...)`, with `# nosec B603, B607` justification comments.
- Issue #61 was created at 2026-09-15 15:54:32 UTC; PR #78 merged at 17:38 UTC the same day.
- The sibling issue #68 (`scope.py:36`, same pattern) was closed as already fixed for the same reason.

## Implementation Steps

### Step 1 — Verify the current state of `scope.py`
Confirm that every `subprocess.run` call in `python/kube/scope.py` (`switch_context` x2, `list_available_contexts`, `detect_active_scope`) passes `binaries.resolve("<name>")` as the executable rather than a bare string, and that no bare-name executable remains. Run the python lint and test suites to confirm the tree is green. No file is edited.

### Step 2 — Close the issue as already fixed
No code change and no PR diff is expected. Close GitHub issue #61 as superseded by #58 / PR #78, noting that a fresh Codacy re-scan should stop reporting the finding. If the re-scan still reports `Bandit_B607` on a line that is actually a `binaries.resolve(...)` call, open a separate follow-up issue about the Codacy pattern configuration rather than reworking `scope.py`.

## Files to Change
- None. `python/kube/scope.py` already contains the fix.

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- The line number in the Codacy finding (46) no longer points at a subprocess call, which is further evidence the scan was against pre-fix code.
- Nothing here needs a specialist agent, since no file under `python/` changes.
