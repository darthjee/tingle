# Python Plan: Codacy: Missing blank line after last section ('Examples') (D413) (python/check_file_size/executor.py:2)

Main plan: [plan.md](plan.md)

## Overview
This is a docstring-only fix in `python/check_file_size/executor.py`. Rewrite the module docstring's `Examples` section so it passes Codacy's pydocstyle checks, which use Numpy conventions. One edit clears three findings on the same lines: D406 (#131), D407 (#130) and D413 (#129).

## Context
The module docstring (lines 2–18) currently ends with:

```
Examples:
    ./check_file_size.py ./src
    ./check_file_size.py ./src --warn 300 --error 500 --critical 1000
    ./check_file_size.py ./src --top 20
    ./check_file_size.py ./src --exclude node_modules,dist,build
    ./check_file_size.py ./src --ext .py --ext .js
"""
```

Codacy reports:
- **D406:** the section name ends with `:`.
- **D407:** there is no dashed underline after the section header.
- **D413:** there is no blank line after the last section.

Nothing in `python/` reads `__doc__`, so the change has no runtime effect and does not change `--help` output.

## Implementation Steps

### Step 1 — Rewrite the `Examples` section in Numpy style
In the module docstring of `python/check_file_size/executor.py`:
- change the header `Examples:` to `Examples`, with no colon;
- add a line `--------` right below the header (8 dashes, matching the header length);
- keep the five example lines unchanged, with their 4-space indentation;
- add one blank line between the last example line and the closing `"""`.

The result:

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

Leave the rest of the docstring as it is, including the summary line, the description paragraph and the `Usage:` block. `Usage` is not a section name pydocstyle recognizes, and D212 (where the summary line starts) is not flagged for this file.

## Files to Change
- `python/check_file_size/executor.py` — rewrite the module docstring's `Examples` section: remove the colon, add the dashed underline, add a trailing blank line.

## CI Checks
- `python`: `cd python && ruff check .` (CI job: `lint`)
- `python`: `cd python && pytest` (CI job: `tests`)

## Notes
- The PR description must close all three issues: `Fixes #129`, `Fixes #130`, `Fixes #131`.
- The repo's ruff config does not enable pydocstyle (`D`) rules, so ruff won't conflict with the Numpy-style header.
- Optional local check: `pydocstyle --convention=numpy python/check_file_size/executor.py` (or `--select=D406,D407,D413`) should report no findings for the module docstring.
