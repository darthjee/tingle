# Issue: Codacy: Missing docstring in __init__ (D107) (python/check_file_size/file_collector.py:13)

## Description
Codacy's Prospector (pydocstyle) flagged `python/check_file_size/file_collector.py:13` (pattern `Prospector_pydocstyle`, category Documentation): "Missing docstring in __init__ (D107)" on:

```
    def __init__(self, excludes: list[str], extensions: list[str] | None):
```

## Problem
The `FileCollector.__init__` method had no docstring, which pydocstyle's D107 rule requires.

## Expected Behavior
`FileCollector.__init__` has a docstring, satisfying pydocstyle D107.

## Solution
Already resolved on `main`: commit `11083f2` (PR #149, "Fix #141 — Missing docstring in __init__ (D107)") added the docstring below to `python/check_file_size/file_collector.py:14` alongside its fix for `python/kube/config.py`:

```python
def __init__(self, excludes: list[str], extensions: list[str] | None):
    """Store case-insensitive exclusions and optional extension filters (`None`: no filter)."""
```

No further code change is needed; this issue should be closed as already fixed by #149.
