# Plan: Multi-line docstring summary should start at the first line (D212) (python/kube/binaries.py:1)

Issue: [154-multi-line-docstring-summary-should-start-at-the-first-line-d212-python-kube-binaries-py-1.md](../../issues/154-multi-line-docstring-summary-should-start-at-the-first-line-d212-python-kube-binaries-py-1.md)

## Overview
Join the opening `"""` and the summary line of the module docstring in `python/kube/binaries.py` so it satisfies pydocstyle D212 ("multi-line docstring summary should start at the first line"). Formatting-only change; no behavior changes.

## Context
`python/kube/binaries.py` currently begins:

```python
"""
binaries.py — Executable path resolution for kube.

Resolves a bare executable name ...
```

D212 expects the summary on the same line as the opening quotes. The same fix was applied to `python/kube/matching.py` (#139) and `python/kube/inventory.py` (#157). The two other modules still in this shape, `python/kube/configure.py` and `python/kube/parser.py`, are tracked separately in #155 and #156 and are out of scope.

## Implementation Steps

### Step 1 — Join the docstring's first two lines
Change lines 1–2 of `python/kube/binaries.py` from:

```python
"""
binaries.py — Executable path resolution for kube.
```

to:

```python
"""binaries.py — Executable path resolution for kube.
```

Leave the blank line after the summary, the description body, and the closing `"""` unchanged (that keeps D205 and D415 satisfied too, since the summary still ends with a period).

### Step 2 — Verify
From `python/`, run `ruff check .` and `pytest` and confirm both pass unchanged.

## Files to Change
- `python/kube/binaries.py` — join lines 1–2 of the module docstring (D212).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Pure formatting change; no tests need to be added or updated.
