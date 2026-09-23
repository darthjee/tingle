# Plan: Codacy: Missing docstring in __init__ (D107) (python/check_file_size/file_collector.py:13)

Issue: [127-codacy-missing-docstring-in-init-d107-python-check-file-size-file-collector-py-13.md](../../issues/127-codacy-missing-docstring-in-init-d107-python-check-file-size-file-collector-py-13.md)

## Overview
Verify that `FileCollector.__init__` in `python/check_file_size/file_collector.py` already carries a docstring, so the Codacy D107 finding is resolved without further code changes.

## Context
Codacy flagged `python/check_file_size/file_collector.py:13` with "Missing docstring in __init__ (D107)". Commit `11083f2` (PR #149, fixing #141) already added the docstring:

```python
def __init__(self, excludes: list[str], extensions: list[str] | None):
    """Store case-insensitive exclusions and optional extension filters (`None`: no filter)."""
```

## Implementation Steps

### Step 1 — Verify the docstring is present
Confirm `python/check_file_size/file_collector.py` still has the `__init__` docstring shown above. Do not modify the source file. If it is somehow missing, restore it in this same form.

## Files to Change
- None — the fix already landed on `main` via PR #149.

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- The GitHub issue should be closed as already fixed by #149; Codacy's next analysis of `main` should clear the finding.
