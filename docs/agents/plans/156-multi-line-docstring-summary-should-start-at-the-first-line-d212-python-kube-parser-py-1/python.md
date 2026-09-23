# Python Plan: Multi-line docstring summary should start at the first line (D212) (python/kube/parser.py:1)

Main plan: [plan.md](plan.md)

## Overview
Join lines 1–2 of the module docstring in `python/kube/parser.py` so the summary directly follows the opening `"""`. This is the same change made to `python/kube/binaries.py` in #154 and to `python/kube/matching.py` in #139.

## Context
Line 1 of `python/kube/parser.py` holds only `"""` and the summary `parser.py — Subcommand-aware argument parser for kube.` is on line 2. pydocstyle D212 (run by Codacy's Prospector) expects the summary on the first line. Codacy hasn't reported this file yet; it was found while refining #137.

## Implementation Steps

### Step 1 — Join the docstring's opening lines
Replace:

```python
"""
parser.py — Subcommand-aware argument parser for kube.
```

with:

```python
"""parser.py — Subcommand-aware argument parser for kube.
```

Leave the rest of the docstring (the blank line, body paragraph, and `Usage:` block) and all code untouched.

## Files to Change
- `python/kube/parser.py` — move the module docstring summary onto line 1 (D212).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Docstring-only change; nothing at runtime changes and no tests need updating.
- The function/method docstrings in `parser.py` are already one-liners, so they don't trigger D212.
