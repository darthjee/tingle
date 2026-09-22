# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/auth.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/auth.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)"

## Problem
The module docstring in `python/kube/auth.py` opens with `"""` alone on line 1, with the summary (`auth.py — AWS credential pre-check for kube.`) on line 2. pydocstyle's D212 rule expects the summary to start on the same line as the opening quotes.

## Expected Behavior
The module docstring starts with `"""auth.py — AWS credential pre-check for kube.` on line 1, satisfying D212. The rest of the docstring body is unchanged.

## Solution
Merge lines 1–2 of `python/kube/auth.py` so the summary follows the opening `"""` directly — the same one-line change applied to `python/kube/matching.py` in #139. No code or behavior changes.

Scope is limited to `auth.py`; the same D212 pattern in other modules (`exec.py`, `completion.py`, `scope.py`, etc.) is tracked by separate issues (#134, #135, #136).

## Benefits
Resolves the Codacy finding and keeps docstring formatting consistent across the codebase.
