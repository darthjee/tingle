# Issue: Codacy: Missing docstring in public package (D104) (python/kube/__init__.py:1)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/__init__.py:1` (pattern `Prospector_pydocstyle`, category Documentation): "Missing docstring in public package (D104)".

The same finding was reported for every other empty package `__init__.py` under `python/`, tracked in #119–#124. This issue covers all of them in a single change:

| Issue | File |
|-------|------|
| #118 | `python/kube/__init__.py` |
| #119 | `python/tests/__init__.py` |
| #120 | `python/common/__init__.py` |
| #121 | `python/tests/check_file_size/__init__.py` |
| #122 | `python/tests/common/__init__.py` |
| #123 | `python/tests/kube/__init__.py` |
| #124 | `python/check_file_size/__init__.py` |

## Problem
All seven `__init__.py` files are currently empty. pydocstyle's D104 rule requires every public package's `__init__.py` to have a module-level docstring.

## Expected Behavior
Each of the seven `__init__.py` files contains a short module-level docstring describing its package, and Codacy/pydocstyle no longer reports D104 for any of them. No runtime behavior changes.

## Solution
Add a single one-line docstring to each file, in the same `"""<name> — <purpose>."""` style the package modules already use (e.g. `"""scope.py — Context alias resolution ..."""`). For example:

- `python/kube/__init__.py` → `"""kube — Kubernetes context/namespace helper: flow-verb CLI, scope resolution and command execution."""`
- `python/common/__init__.py` → `"""common — Shared, reusable helpers (e.g. argument parsing) for the Python scripts."""`
- `python/check_file_size/__init__.py` → `"""check_file_size — Token efficiency triage: file size analysis."""`
- `python/tests/__init__.py` → `"""tests — Test suite for the Python scripts."""`
- `python/tests/<pkg>/__init__.py` → `"""tests.<pkg> — Tests for the <pkg> package."""`

Only the docstring goes in each file. Do not add imports or other code.

The PR must close #119, #120, #121, #122, #123 and #124 along with #118 (for example with `Closes #119` lines in the PR description).

## Benefits
Clears all seven D104 findings in one PR instead of seven, and gives readers/agents a quick overview of each package.
