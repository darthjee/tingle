# Issue: Codacy: Missing blank line after last section ('Examples') (D413) (python/check_file_size/executor.py:2)

## Description
Codacy's Prospector (pydocstyle) flagged `python/check_file_size/executor.py:2` (pattern `Prospector_pydocstyle`, category Documentation): "Missing blank line after last section ('Examples') (D413)".

The same `Examples` section is also flagged by two sibling issues, which this issue absorbs:
- #130: Missing dashed underline after section ('Examples') (D407)
- #131: Section name should end with a newline ('Examples', not 'Examples:') (D406)

## Problem
The module docstring of `python/check_file_size/executor.py` writes its `Examples` section in Google style (`Examples:`), but Codacy checks sections against Numpy conventions:
- the header ends with a colon (D406);
- the header has no dashed underline (D407);
- the last entry (`./check_file_size.py ./src --ext .py --ext .js`) runs straight into the closing `"""` with no blank line (D413).

All three findings are on the same few lines, so fixing them in separate PRs would mean overlapping edits to the same lines, and each intermediate state would still be flagged.

## Expected Behavior
The `Examples` section follows Numpy section formatting, and Codacy no longer reports D406, D407 or D413 for `python/check_file_size/executor.py`. Only the docstring changes: the script's runtime behavior and `--help` output stay the same, since nothing reads `__doc__`.

## Solution
Rewrite the `Examples` section of the module docstring in `python/check_file_size/executor.py` as:

```
Examples
--------
    ./check_file_size.py ./src
    ./check_file_size.py ./src --warn 300 --error 500 --critical 1000
    ./check_file_size.py ./src --top 20
    ./check_file_size.py ./src --exclude node_modules,dist,build
    ./check_file_size.py ./src --ext .py --ext .js

"""
```

- Drop the colon from the header (D406).
- Add a dashed underline as long as the header, `--------` (D407).
- Add a blank line between the last entry and the closing `"""` (D413).

The PR must close all three issues (`Fixes #129`, `Fixes #130`, `Fixes #131`).

Out of scope:
- `Usage:` is not a section name pydocstyle recognizes and isn't flagged, so it stays unchanged.
- The summary starts on the line after the opening `"""`. Codacy hasn't flagged D212 for this file, so that is not changed here.

## Benefits
One small docstring-only PR resolves three Codacy findings and leaves the `Examples` section fully compliant. It avoids three overlapping PRs on the same lines.
