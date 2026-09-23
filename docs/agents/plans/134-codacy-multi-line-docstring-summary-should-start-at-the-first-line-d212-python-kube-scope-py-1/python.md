# Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/scope.py:1)

Issue: [134-codacy-multi-line-docstring-summary-should-start-at-the-first-line-d212-python-kube-scope-py-1.md](../../issues/134-codacy-multi-line-docstring-summary-should-start-at-the-first-line-d212-python-kube-scope-py-1.md)

## Overview
Fix the Codacy/pydocstyle D212 finding on `python/kube/scope.py:1` by starting the module docstring summary on the same line as the opening `"""`.

## Context
The module docstring currently opens with a bare `"""` on line 1 and places the summary
(`scope.py — Context alias resolution and active-scope detection for kube.`) on line 2.
D212 requires the summary to start on the first line. The same fix was already applied to
`python/kube/completion.py` (#136), `auth.py` (#137), `validation.py` (#138),
`matching.py` (#139) and `config.py` (#140). The function docstrings in `scope.py`
already comply.

## Implementation Steps

### Step 1 — Join the summary to the opening quotes
Change lines 1–2 of `python/kube/scope.py` from:

```python
"""
scope.py — Context alias resolution and active-scope detection for kube.
```

to:

```python
"""scope.py — Context alias resolution and active-scope detection for kube.
```

Leave the rest of the docstring (blank line, body paragraph, closing `"""`) unchanged.
No behavior change.

## Files to Change
- `python/kube/scope.py` — move the module docstring summary onto the opening `"""` line.

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- Documentation-only change; no tests need updating.
