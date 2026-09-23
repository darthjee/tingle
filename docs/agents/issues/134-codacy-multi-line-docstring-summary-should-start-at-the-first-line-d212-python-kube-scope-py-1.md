# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/scope.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/scope.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)"

## Problem
The module docstring in `python/kube/scope.py` opens with a blank first line before its summary text, which pydocstyle's D212 rule flags — it expects the summary to start on the same line as the opening `"""`.

## Expected Behavior
The module docstring in `python/kube/scope.py` starts its summary text on the same line as the opening `"""`, satisfying pydocstyle D212.

## Solution
Edit the module docstring at the top of `python/kube/scope.py` so the summary sentence begins immediately after the opening `"""` (same line), rather than on the following line.

## Benefits
Resolves the Codacy finding and keeps docstring formatting consistent across the codebase.

