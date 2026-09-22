# Issue: Codacy: Missing docstring in __init__ (D107) (python/kube/config.py:24)

## Description
Codacy's Prospector (pydocstyle) flagged `python/kube/config.py:24` (pattern `Prospector_pydocstyle`, category Documentation): "Missing docstring in __init__ (D107)" on:

```
    def __init__(self, path: Path | None = None):
```

The same gap exists in every other constructor under `python/`, which would trigger the same D107 finding. This issue covers all of them in one pass instead of one issue per finding.

## Problem
The following `__init__` methods have no docstring, which pydocstyle's D107 rule requires:

- `python/kube/config.py:24` — `KubeConfig.__init__(self, path: Path | None = None)`
- `python/check_file_size/reporter.py:14` — `Reporter.__init__(self, analyzer: FileAnalyzer, target: Path)`
- `python/check_file_size/file_analyzer.py:13` — `FileAnalyzer.__init__(self, warn: int, error: int, critical: int)`
- `python/check_file_size/file_collector.py:13` — `FileCollector.__init__(self, excludes: list[str], extensions: list[str] | None)`
- `python/common/arg_parser.py:18` — `ArgParser.__init__(self, flags: list[dict])`

## Expected Behavior
Every `__init__` under `python/` has a short docstring describing what it initializes (its parameters at a high level), satisfying pydocstyle D107. No `__init__` under `python/` is left undocumented.

In particular, `KubeConfig.__init__`'s docstring should mention that `path` defaults to `Constants.CONFIG_PATH` and that the config is loaded immediately on construction. Loading can create a fresh config file on disk if none exists (via `_bootstrap`), or flag pass-through mode on failure.

## Solution
Add a concise docstring to each of the five constructors listed above. Match the style already used in these modules: a one-line summary in imperative mood (e.g. `"""Load ~/.tingle/kube/config.json, validating and defaulting it."""`), plus a short body only where there is a non-obvious side effect (as in `KubeConfig.__init__`). The change is documentation only, with no behavior changes. All files are under `python/`, so this is owned by the `python` agent.

## Benefits
Resolves the current Codacy D107 finding and prevents four equivalent follow-up findings. It also documents each constructor's parameters and, for `KubeConfig`, its on-construction side effects, for future readers.
