# Python Plan: Codacy: Missing docstring in __init__ (D107) (python/kube/config.py:24)

Main plan: [plan.md](plan.md)

## Overview
Every `__init__` under `python/` has no docstring, which pydocstyle's D107 rule requires. Add a concise docstring to each one, following the existing docstring style of the surrounding modules.

## Context
- Class and method docstrings in these modules use a one-line, imperative-mood summary on the same line as the opening quotes (e.g. `"""Count lines and classify files by threshold."""`). They use a multi-line body only when there is a non-obvious detail (e.g. `KubeConfig.save`).
- `KubeConfig.__init__` has side effects on construction: `path` falls back to `Constants.CONFIG_PATH`, and `self._load()` runs immediately. Loading may create a fresh config file on disk (`_bootstrap`) or flag pass-through mode with a `notice` (`_fallback`), and it never raises for a bad config.
- The other four constructors only store (or normalize) their arguments.

## Implementation Steps

### Step 1 — Add constructor docstrings
Add a docstring as the first statement of each `__init__` below. Suggested wording (adjust freely, keeping it short):

- `python/kube/config.py:24` — `KubeConfig.__init__`: multi-line docstring, e.g.
  ```python
  """Load and validate the config at `path` (default: `Constants.CONFIG_PATH`).

  Loading happens immediately: a missing file is bootstrapped on disk,
  while an unreadable or invalid one flags pass-through mode (see
  `pass_through` / `notice`) instead of raising.
  """
  ```
- `python/check_file_size/reporter.py:14` — `Reporter.__init__`: e.g. `"""Store the analyzer used to classify results and the target being reported on."""`
- `python/check_file_size/file_analyzer.py:13` — `FileAnalyzer.__init__`: e.g. `"""Store the warn/error/critical line-count thresholds."""`
- `python/check_file_size/file_collector.py:13` — `FileCollector.__init__`: e.g. `"""Store case-insensitive exclusions and optional extension filters."""` (note `extensions=None` means no extension filter)
- `python/common/arg_parser.py:18` — `ArgParser.__init__`: e.g. `"""Store the flag-definition dicts used to build the parser."""`

Keep lines within the project's ruff line-length limit.

## Files to Change
- `python/kube/config.py` — docstring on `KubeConfig.__init__`
- `python/check_file_size/reporter.py` — docstring on `Reporter.__init__`
- `python/check_file_size/file_analyzer.py` — docstring on `FileAnalyzer.__init__`
- `python/check_file_size/file_collector.py` — docstring on `FileCollector.__init__`
- `python/common/arg_parser.py` — docstring on `ArgParser.__init__`

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- Before finishing, re-check with `grep -rn -A1 "def __init__" python/` that no undocumented `__init__` remains (the issue's expected behavior is "none left").
- Documentation only; no tests need to change.
