# Python Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/completion.py:1)

Main plan: [plan.md](plan.md)

## Overview
Whitespace-only fix to the module docstring of `python/kube/completion.py` so its summary line starts right after the opening `"""`, resolving the Codacy pydocstyle D212 finding.

## Context
Line 1 of `python/kube/completion.py` currently holds only `"""`, and the summary `completion.py — Bash-completion candidate resolution for kube.` is on line 2. D212 requires the summary on the first line. Identical fixes were already merged for `validation.py` (#138), `matching.py` (#139) and `config.py` (#140).

## Implementation Steps

### Step 1 — Join the docstring opening and summary lines
Replace the first two lines:

```python
"""
completion.py — Bash-completion candidate resolution for kube.
```

with:

```python
"""completion.py — Bash-completion candidate resolution for kube.
```

Leave the rest of the docstring body (and all code) untouched.

## Files to Change
- `python/kube/completion.py` — merge the docstring's opening `"""` and summary into line 1.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- No behavior change; tests should pass unchanged.
