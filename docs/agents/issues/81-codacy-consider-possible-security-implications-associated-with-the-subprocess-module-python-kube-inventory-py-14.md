# Issue: Codacy: Consider possible security implications associated with the subprocess module. (python/kube/inventory.py:14)

## Description
Codacy/Bandit flagged the `import subprocess` statement in `python/kube/inventory.py:14` under rule `B404` (category: Security, severity: Info): "Consider possible security implications associated with the subprocess module." Codacy issue ID `556434f2fe067875c3bd7dd4b8dcae4f`.

This is one of four sibling findings for the same Bandit rule (`B404`) reported across every file in `python/kube` that imports `subprocess`: `inventory.py:14` (this issue, #81), `exec.py:14` (#76), `scope.py:13` (#82), and `auth.py:14` (#83).

## Problem
`B404` is a blanket warning Bandit raises on the `import subprocess` statement itself, independent of how the module is used afterward. The `subprocess.run(...)` call sites inside these files already carry `# nosec B603, B607` justifications (added by the prior fixes for issues #57/#58: fixed binary resolved via `binaries.resolve()`, list-form arguments, no shell) — but those suppressions only cover the call-site checks (`B603`/`B607`), not the import-level `B404` finding, which remains open on all four files.

## Solution
Add a `# nosec B404` suppression comment to the `import subprocess` line in `python/kube/inventory.py`, `exec.py`, `scope.py`, and `auth.py`, with a short rationale consistent with this repo's existing `nosec` comment style (the `B603`/`B607` comments already on these files' call sites, and the `B105` comments in `python/kube/completion.py`) — noting that subprocess usage in this module is confined to fixed CLI binaries invoked via `binaries.resolve()` with list-form arguments and no shell.

Mirroring the precedent set by issues #57/#58 (single Codacy-reported issue, fix applied across all four files sharing the pattern in one PR), this fix should be batched across all four sibling `B404` findings — #81 (this issue), #76 (`exec.py`), #82 (`scope.py`), and #83 (`auth.py`) — in a single PR that closes all four.

## Benefits
Clears all four low-severity Codacy `B404` findings in `python/kube` in one pass without changing runtime behavior, keeping each file's Bandit-suppression comments complete at both the import level and the call-site level.
