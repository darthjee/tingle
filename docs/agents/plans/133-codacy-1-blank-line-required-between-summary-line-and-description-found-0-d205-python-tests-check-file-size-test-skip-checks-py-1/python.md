# Python Plan: Codacy: 1 blank line required between summary line and description (found 0) (D205) (python/tests/check_file_size/test_skip_checks.py:1)

Main plan: [plan.md](plan.md)

## Overview
Reformat the module docstring of `python/tests/check_file_size/test_skip_checks.py` so pydocstyle D205 (and D400) pass. This is a docstring-only change.

## Context
The current docstring runs one sentence over three lines, with no blank line after a summary line:

```python
"""Unit tests for check_file_size.skip_checks.SkipChecks, plus the --top 0
and default-exclude edge cases that live at the FileCollector/CheckFileSize
level.
"""
```

## Implementation Steps

### Step 1 — Rewrite the module docstring
Replace lines 1–4 with:

```python
"""Unit tests for check_file_size.skip_checks.SkipChecks.

Also covers the --top 0 and default-exclude edge cases that live at the
FileCollector/CheckFileSize level.
"""
```

Leave all code and tests below the docstring untouched.

## Files to Change
- `python/tests/check_file_size/test_skip_checks.py` — module docstring only (lines 1–4).

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Keep the summary line under the line-length limit. No behavior change is expected.
