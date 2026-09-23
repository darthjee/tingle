# Python Plan: Multi-line docstring summary should start at the first line (D212) (python/common/arg_parser.py:1)

Main plan: [plan.md](plan.md)

## Overview
Fix the D212 shape of the module docstring in `python/common/arg_parser.py`: the opening `"""` sits alone on line 1 and the summary is on line 2.

## Context
Codacy (Prospector/pydocstyle) flagged the same shape as D212 in several `python/kube` modules (#134–#140, #157), all fixed by the same one-line join. `arg_parser.py` has not been reported yet, but has the identical shape. The remaining `python/kube` offenders (`binaries.py`, `configure.py`, `parser.py`) are tracked in #154–#156 and are out of scope here.

## Implementation Steps

### Step 1 — Join the docstring's first two lines
Change the top of `python/common/arg_parser.py` from:

```python
"""
arg_parser.py — Generic, reusable command-line argument parser.
```

to:

```python
"""arg_parser.py — Generic, reusable command-line argument parser.
```

Leave the rest of the docstring (blank line, description paragraph, closing `"""`) and all code unchanged.

## Files to Change
- `python/common/arg_parser.py` — move the docstring summary onto line 1, right after the opening `"""`.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- No behavior change; no test changes expected.
