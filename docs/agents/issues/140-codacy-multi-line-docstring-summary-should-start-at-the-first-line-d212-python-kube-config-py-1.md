# Issue: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/config.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/config.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Multi-line docstring summary should start at the first line (D212)"

## Problem
The module docstring in `python/kube/config.py` opens with a bare `"""` line, putting its summary (`config.py — Load, validate, and default ~/.tingle/kube/config.json.`) on the following line. pydocstyle's D212 rule expects the summary to start on the same line as the opening `"""`.

## Expected Behavior
The module docstring in `python/kube/config.py` starts its summary text on the same line as the opening `"""`, satisfying pydocstyle D212, with the docstring's wording and body paragraph otherwise unchanged.

## Solution
Move the summary line up so it directly follows the opening `"""` (e.g. `"""config.py — Load, validate, and default ~/.tingle/kube/config.json.`), keeping the blank line and body paragraph after it as-is. This matches the single-line-summary style already used by the rest of the Python code (e.g. `python/check_file_size/reporter.py`).

Scope is limited to `python/kube/config.py`. The same D212 pattern exists in other modules (e.g. `matching.py`, `validation.py`, `auth.py`, `completion.py`, `exec.py`, `scope.py`), but those are tracked by their own sibling issues (#134–#139) and must not be touched here.

## Benefits
Resolves the Codacy finding and keeps docstring formatting consistent across the codebase.
