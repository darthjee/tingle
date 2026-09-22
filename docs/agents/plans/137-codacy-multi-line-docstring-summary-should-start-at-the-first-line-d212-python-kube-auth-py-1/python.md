# Python Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/auth.py:1)

Main plan: [plan.md](plan.md)

## Overview
Fix the D212 Codacy finding in `python/kube/auth.py` by moving the module docstring summary onto line 1, right after the opening `"""`.

## Context
Codacy's Prospector (pydocstyle) flagged `python/kube/auth.py:1` with D212. Right now line 1 is just `"""` and the summary `auth.py — AWS credential pre-check for kube.` is on line 2. The same fix was already applied to `python/kube/matching.py` in #139 (commit c3271d9).

## Implementation Steps

### Step 1 — Merge the docstring's opening lines
Replace the first two lines of `python/kube/auth.py`:

```python
"""
auth.py — AWS credential pre-check for kube.
```

with:

```python
"""auth.py — AWS credential pre-check for kube.
```

Leave the rest of the docstring (blank line, body paragraph, closing `"""`) and all code unchanged.

## Files to Change
- `python/kube/auth.py` — join docstring lines 1–2 (D212).

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- Only `auth.py` is in scope. Other modules with the same pattern are tracked separately (#134, #135, #136) or not yet reported.
- Documentation-only change; no behavior or test changes expected.
