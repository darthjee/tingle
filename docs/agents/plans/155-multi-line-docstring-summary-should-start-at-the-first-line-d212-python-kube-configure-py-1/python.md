# Python Plan: Multi-line docstring summary should start at the first line (D212) (python/kube/configure.py:1)

Main plan: [plan.md](plan.md)

## Overview
Make the module docstring of `python/kube/configure.py` satisfy pydocstyle D212 by moving its summary onto the opening-quotes line.

## Context
`python/kube/configure.py` opens with `"""` alone on line 1 and the summary on line 2. Codacy's Prospector has flagged this exact shape as D212 in sibling modules; it has not flagged this file yet, but will. The identical one-line fix was already merged for `python/kube/inventory.py` (#157) and `python/common/arg_parser.py` (#153).

## Implementation Steps

### Step 1 — Join the docstring's opening lines
Replace lines 1–2:

```python
"""
configure.py — Interactive `configure context|namespace|pod` flows for kube.
```

with a single line:

```python
"""configure.py — Interactive `configure context|namespace|pod` flows for kube.
```

Leave the blank line, the rest of the docstring body, and the closing `"""` untouched.

## Files to Change
- `python/kube/configure.py` — join docstring lines 1–2 so the summary follows the opening `"""`.

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- Pure formatting change; no tests need adding or updating.
- Do not touch any other docstrings in the file — scope is line 1 only.
