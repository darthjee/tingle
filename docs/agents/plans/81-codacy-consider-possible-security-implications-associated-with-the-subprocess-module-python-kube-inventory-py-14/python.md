# Python Plan: Codacy: Consider possible security implications associated with the subprocess module. (python/kube/inventory.py:14)

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Suppress `B404` on the `import subprocess` lines
Add a `# nosec B404` comment to the `import subprocess` statement in each of the four `python/kube` files that import it, with a short inline rationale consistent with this repo's existing `nosec` comment style (the `# nosec B603, B607 - fixed binary, list-form args, no shell` comments already on these files' `subprocess.run` call sites, added by issues #57/#58, and the `# nosec B105 - CLI flag literal, not a credential` comments in `python/kube/completion.py`).

Example, applied identically to all four files:

```python
import subprocess  # nosec B404 - usage confined to fixed CLI binaries via binaries.resolve(), list-form args, no shell
```

This closes issue #81 (this issue) plus its three live siblings for the same `B404` finding: #76 (`exec.py`), #82 (`scope.py`), #83 (`auth.py`).

### Step 2 — Verify no regressions
Run the local lint and test commands (see `## CI Checks` below) to confirm the comment-only change doesn't break `ruff` (which also parses `# nosec`-style trailing comments) or the existing test suite for these four modules.

## Files to Change
- `python/kube/inventory.py` — add `# nosec B404` rationale comment to the `import subprocess` line (closes #81).
- `python/kube/exec.py` — add `# nosec B404` rationale comment to the `import subprocess` line (closes #76).
- `python/kube/scope.py` — add `# nosec B404` rationale comment to the `import subprocess` line (closes #82).
- `python/kube/auth.py` — add `# nosec B404` rationale comment to the `import subprocess` line (closes #83).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Comment-only change on the import line; no runtime behavior changes, so no test updates are expected — `test_inventory.py`, `test_exec.py`, `test_scope.py`, and `test_auth.py` should pass unmodified.
- Bandit itself isn't run as part of local CI (`ruff`/`pytest` only) — the `B404` suppression is verified indirectly via the next Codacy scan of the PR, same as the prior `B603`/`B607`/`B105` fixes.
