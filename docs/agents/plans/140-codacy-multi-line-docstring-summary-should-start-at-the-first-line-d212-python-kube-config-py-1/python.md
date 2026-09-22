# Python Plan: Codacy: Multi-line docstring summary should start at the first line (D212) (python/kube/config.py:1)

Main plan: [plan.md](plan.md)

## Overview
Fix the pydocstyle D212 finding on the module docstring of `python/kube/config.py` by starting the summary on the same line as the opening `"""`.

## Context
The module docstring currently opens with a bare `"""` on line 1 and places the summary (`config.py — Load, validate, and default ~/.tingle/kube/config.json.`) on line 2. Codacy's Prospector (pydocstyle) flags this as D212. Most other Python modules (e.g. `python/check_file_size/reporter.py`) already use the first-line-summary style.

## Implementation Steps

### Step 1 — Move the summary onto the opening line
Rewrite lines 1–2 of `python/kube/config.py` so the docstring begins:

```python
"""config.py — Load, validate, and default ~/.tingle/kube/config.json.

Reads the config file, validates its shape against the schema in
...
"""
```

Keep the summary wording, the blank line after it, the body paragraph, and the closing `"""` unchanged. No code changes.

## Files to Change
- `python/kube/config.py` — module docstring: summary moved onto the opening `"""` line.

## CI Checks
- `python`: `cd python && ruff check . && pytest` (CI jobs: `lint`, `tests`)

## Notes
- Scope is limited to `python/kube/config.py`. Other modules with the same D212 pattern (`matching.py`, `validation.py`, `auth.py`, `completion.py`, `exec.py`, `scope.py`, etc.) are tracked by sibling issues (#134–#139) and must not be touched here.
- Leave the other docstrings in the file (e.g. `KubeConfig.__init__`) alone; they already comply.
