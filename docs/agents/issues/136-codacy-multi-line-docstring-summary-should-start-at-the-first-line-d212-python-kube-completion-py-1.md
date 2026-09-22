# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/completion.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/completion.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)"

## Problem
The module docstring in `python/kube/completion.py` opens with `"""` alone on line 1, with the summary (`completion.py — Bash-completion candidate resolution for kube.`) on line 2. pydocstyle's D212 rule expects the summary to start on the same line as the opening quotes.

## Expected Behavior
The module docstring's summary starts on the same line as the opening `"""` (e.g. `"""completion.py — Bash-completion candidate resolution for kube.`), satisfying D212. The rest of the docstring body is unchanged.

## Solution
Merge the first two lines of the module docstring in `python/kube/completion.py` so the summary follows the opening `"""` directly. This is a whitespace-only change with no behavior impact, matching the fixes already merged for `validation.py` (#138), `matching.py` (#139) and `config.py` (#140).

## Benefits
Resolves the Codacy finding and keeps docstring formatting consistent across the `python/kube` modules.
