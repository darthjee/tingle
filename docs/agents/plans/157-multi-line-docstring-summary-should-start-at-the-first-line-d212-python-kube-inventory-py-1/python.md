# Python Plan: Multi-line docstring summary should start at the first line (D212) (python/kube/inventory.py:1)

Main plan: [plan.md](plan.md)

## Overview
Formatting-only fix to the module docstring of `python/kube/inventory.py` so it satisfies pydocstyle D212, the same change already applied to `scope.py` (#134) and `matching.py` (#139).

## Context
The module docstring opens with `"""` alone on line 1 and places the summary on line 2. D212 requires the summary to start on the first line. Codacy has not flagged this file yet; the fix is preventive.

## Implementation Steps

### Step 1 — Move the docstring summary onto the opening line
Replace lines 1–2:

```python
"""
inventory.py — Kubectl inventory helpers for kube.
```

with:

```python
"""inventory.py — Kubectl inventory helpers for kube.
```

Leave the blank line after the summary and the rest of the docstring untouched (keeps D205 and D400/D415 satisfied). No code or behavior changes.

## Files to Change
- `python/kube/inventory.py` — join docstring lines 1–2 (D212).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- `binaries.py`, `configure.py`, `parser.py` and `common/arg_parser.py` are tracked separately (#153–#156); `executor.py` and `main.py` have the same shape after a shebang but are out of scope here.
