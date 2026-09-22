# Python Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/matching.py:1)

Main plan: [plan.md](plan.md)

## Overview
Codacy (Prospector/pydocstyle) flags `python/kube/matching.py:1` with D212 because the module docstring's summary starts on the line after the opening `"""`. Join the two lines. The docstring text does not change.

## Context
The file currently starts with:

```python
"""
matching.py — Pod-matching pipeline for kube discovery.

Standalone, reusable filter/sort pipeline: ...
"""
```

#140 applied the same fix to `python/kube/config.py`, which is now on main (`"""config.py — Load, validate, ...`).

## Implementation Steps

### Step 1 — Join the opening quotes with the summary line
Rewrite lines 1–2 of `python/kube/matching.py` as the single line `"""matching.py — Pod-matching pipeline for kube discovery.`. Keep the blank line after the summary, the extended description paragraph and the closing `"""` exactly as they are. Do not touch the `match_pods` function docstring, which already follows D212.

## Files to Change
- `python/kube/matching.py` — module docstring: the summary moves onto the opening `"""` line (D212).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Scope is this one module docstring only. The other D212 findings (`scope.py`, `exec.py`, `completion.py`, `auth.py`, `validation.py`) are tracked in #134–#138 and must not be changed here.
- The change is behavior-neutral, so no test changes are needed.
