# Issue: Codacy: Function call with shell=True parameter identified, possible security issue (python/tests/kube/test_executor.py:353)

## Description
Codacy's Bandit scan (`Bandit_B604`) flags `python/tests/kube/test_executor.py:353` as "Function call with shell=True parameter identified, possible security issue" (Codacy issue `c97af1849d98eae18c934ff889a69d3b`).

## Problem
This is a false positive. Line 353 (and the identical pattern at line 390) is `shell="bash",` — a keyword argument passed to the test module's `_config()` helper (`python/tests/kube/test_executor.py:12`), which only builds a `MagicMock` config object's `.data` dict. It never reaches `subprocess.run`: the test patches `kube.executor.exec_shell` directly (`@patch("kube.executor.exec_shell")`), so no real process is ever spawned. Bandit's B604 pattern-matcher is tripped by the literal `shell=` text near a call, not by an actual `subprocess.run(..., shell=True)` invocation — the real `exec_shell` implementation in `python/kube/exec.py` already uses list-form args with no `shell=True` (fixed under #65/#66).

## Solution
Suppress the false positive at both occurrences (`test_executor.py:353` and `:390`, both `shell="bash",` inside `_config(...)` calls) with a `# nosec B604 - ...` comment, matching this repo's existing suppression convention (e.g. `python/kube/exec.py:14`), explaining that this is mock config fixture data, not a real `shell=True` subprocess call. Fixing line 390 too, even though Codacy did not flag it, preempts a near-identical future finding on the same false positive.

## Benefits
- Clears the flagged Codacy security finding without changing test behavior.
- Documents, at the point of confusion, why these lines are safe, so they do not get re-flagged or misread as a real vulnerability later.
- Avoids a near-duplicate future Codacy issue on the identical pattern at line 390.
