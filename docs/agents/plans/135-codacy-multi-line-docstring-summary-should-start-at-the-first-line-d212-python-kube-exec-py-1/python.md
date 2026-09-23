# Python Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/exec.py:1)

Main plan: [plan.md](plan.md)

## Overview
Fix the Codacy/Prospector pydocstyle D212 finding at `python/kube/exec.py:1` by starting the module docstring's summary on the same line as the opening `"""`.

## Context
The module docstring currently opens with a bare `"""` line and places the summary `exec.py — Interactive exec and ambiguity-prompt helpers for kube.` on line 2. The identical fix was already applied to `auth.py`, `validation.py`, `matching.py` and `config.py` (#137–#140).

## Implementation Steps

### Step 1 — Join the opening quotes and the summary line
Replace the first two lines of `python/kube/exec.py`:

```python
"""
exec.py — Interactive exec and ambiguity-prompt helpers for kube.
```

with:

```python
"""exec.py — Interactive exec and ambiguity-prompt helpers for kube.
```

Leave the rest of the docstring (blank line, body paragraph, closing `"""`) and the rest of the file untouched.

## Files to Change
- `python/kube/exec.py` — merge docstring lines 1–2 so the summary starts on the first line (D212).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- No behavior change; no tests need to be added or updated.
