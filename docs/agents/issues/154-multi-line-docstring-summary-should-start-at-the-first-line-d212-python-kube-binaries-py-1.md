# Issue: Multi-line docstring summary should start at the first line (D212) (python/kube/binaries.py:1)

## Description
`python/kube/binaries.py:1` has the same module-docstring shape that Codacy's Prospector (pydocstyle) flagged as D212 in other `python/kube` modules (#134–#140). Codacy hasn't reported it yet; it was found during the refinement of #137. The only other modules still in this shape, `python/kube/configure.py` and `python/kube/parser.py`, are tracked separately in #155 and #156 and are out of scope here.

## Problem
The module docstring in `python/kube/binaries.py` opens with `"""` alone on line 1 and puts the summary on line 2. pydocstyle's D212 rule expects the summary to start on the same line as the opening quotes.

## Expected Behavior
The module docstring in `python/kube/binaries.py` starts its summary on the same line as the opening `"""`, satisfying D212.

## Solution
Join lines 1–2 of `python/kube/binaries.py` so the summary follows the opening `"""` directly, the same one-line change made to `python/kube/matching.py` in #139 and `python/kube/inventory.py` in #157. No code or behavior changes.

## Benefits
Prevents a future Codacy finding and keeps docstring formatting consistent across the codebase.
