# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/matching.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/matching.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)".

## Problem
The module docstring in `python/kube/matching.py` has nothing after the opening `"""`. Its summary line (`matching.py — Pod-matching pipeline for kube discovery.`) starts on the next line, which breaks pydocstyle's D212 rule.

## Expected Behavior
The module docstring's summary starts on the same line as the opening `"""`. The extended description paragraph and the closing `"""` stay as they are, so the text does not change.

## Solution
Join the opening `"""` with the summary line so the file starts with `"""matching.py — Pod-matching pipeline for kube discovery.`. This matches the fix already merged for `python/kube/config.py` in #140.

Scope is limited to the module docstring of `python/kube/matching.py`. Other files with the same finding are tracked in their own issues (#134–#138), and the function docstrings in this file already follow D212.

## Benefits
Clears the Codacy finding and keeps module docstrings consistent across `python/kube/`.
