# Python Plan: Codacy: Starting a process with a partial executable path (python/kube/exec.py:27)

## Overview
Codacy's `B607` finding on `python/kube/exec.py:27` is stale: `exec_shell`'s `subprocess.run` call already resolves `kubectl` via `binaries.resolve("kubectl")` (added in issue #58 / PR #78) and carries a `nosec B603, B607` annotation. This plan documents that at the call site, the same fix already applied to `inventory.py` in issue #59, so future re-scans and readers don't re-flag it.

## Context
`exec_shell` in `python/kube/exec.py` calls `subprocess.run([binaries.resolve("kubectl"), "exec", ...], ...)` with a `# nosec B603, B607` comment on the call itself, but has no explanatory comment above it like the three call sites in `inventory.py` do. No functional change is needed — only a comment.

## Implementation Steps

### Step 1 — Add explanatory comment above the `subprocess.run` call in `exec_shell`
Add a two-line comment directly above the `subprocess.run` call inside `exec_shell` (`python/kube/exec.py`), matching the wording used in `inventory.py`:

```python
    # Bandit B607 (partial executable path) resolved via binaries.resolve()
    # in issue #58 / PR #78; see the module docstring for `binaries.py`.
    result = subprocess.run(  # nosec B603, B607 - fixed binary, list-form args, no shell
        [binaries.resolve("kubectl"), "exec", "-n", namespace, "-it", pod, "--", shell],
        check=False,
    )
```

## Files to Change
- `python/kube/exec.py` — add the explanatory comment above the `subprocess.run` call in `exec_shell`; no functional change.

## CI Checks
- `python`: `pytest` (CI job: `tests`)

## Notes
- Purely a documentation/comment change; no behavior, tests, or public API affected.
