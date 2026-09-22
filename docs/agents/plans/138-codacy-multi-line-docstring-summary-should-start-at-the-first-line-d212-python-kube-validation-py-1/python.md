# Python Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/validation.py:1)

Main plan: [plan.md](plan.md)

## Overview
Docstring-only formatting fix in `python/kube/validation.py` to clear Codacy's pydocstyle D212 finding at line 1.

## Context
The module docstring currently opens with a bare `"""` on line 1 and places its summary (`validation.py — Kubernetes resource name validation for kube.`) on line 2. D212 requires the summary to start on the first line. `python/kube/config.py` already uses the compliant style (fixed in #140).

## Implementation Steps

### Step 1 — Join the docstring summary to the opening quotes
Change lines 1–2 of `python/kube/validation.py` from:

```python
"""
validation.py — Kubernetes resource name validation for kube.
```

to:

```python
"""validation.py — Kubernetes resource name validation for kube.
```

Leave the blank line after the summary, the rest of the docstring body, and the closing `"""` unchanged. No code changes.

## Files to Change
- `python/kube/validation.py` — move the module docstring summary onto the opening `"""` line.

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- Scope is limited to this file. The same finding in `scope.py`, `exec.py`, `completion.py` and `auth.py` is tracked in #134–#137; other files with the same pattern are out of scope.
- Function docstrings in `validation.py` already comply; only the module docstring is affected.
