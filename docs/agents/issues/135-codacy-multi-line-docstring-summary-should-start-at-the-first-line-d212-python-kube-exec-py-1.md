# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/exec.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/exec.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)"

## Problem
The module docstring in `python/kube/exec.py` opens with a bare `"""` line, putting its summary (`exec.py — Interactive exec and ambiguity-prompt helpers for kube.`) on the following line. pydocstyle's D212 rule expects the summary to start on the same line as the opening quotes.

## Expected Behavior
The module docstring in `python/kube/exec.py` starts its summary text on the same line as the opening `"""`, satisfying pydocstyle D212. The docstring's wording and the rest of the file are unchanged.

## Solution
Merge the first two lines of the module docstring so it reads:

```python
"""exec.py — Interactive exec and ambiguity-prompt helpers for kube.

Standalone, reusable pieces for the `shell` command: ...
"""
```

This is the same one-line change already applied for the sibling D212 findings in `auth.py`, `validation.py`, `matching.py` and `config.py` (#137–#140). No behavior change and no tests are affected.

## Benefits
Resolves the Codacy finding and keeps module docstring formatting consistent across `python/kube/`.
