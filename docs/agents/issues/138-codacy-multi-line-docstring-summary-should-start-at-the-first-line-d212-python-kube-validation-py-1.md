# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/validation.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/validation.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)"

## Problem
The module docstring in `python/kube/validation.py` opens with a bare `"""` on line 1 and puts its summary (`validation.py — Kubernetes resource name validation for kube.`) on line 2. pydocstyle's D212 rule expects the summary to start on the same line as the opening `"""`.

## Expected Behavior
The module docstring in `python/kube/validation.py` starts its summary text on the same line as the opening `"""`, satisfying pydocstyle D212, matching the style already used in `python/kube/config.py` (fixed in #140).

## Solution
Edit the module docstring at the top of `python/kube/validation.py` so the summary sentence begins immediately after the opening `"""` (same line). The rest of the docstring body stays unchanged; no code changes.

Scope is limited to this file's module docstring (the only D212 offender in it). The same finding in other modules is tracked separately (#134 `scope.py`, #135 `exec.py`, #136 `completion.py`, #137 `auth.py`); other files with the same pattern (e.g. `python/common/arg_parser.py`, `python/kube/configure.py`, `binaries.py`, `parser.py`, `inventory.py`) are out of scope here.

## Benefits
Resolves the Codacy finding and keeps docstring formatting consistent across the codebase.
