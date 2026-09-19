# Plan: Codacy: Function call with shell=True parameter identified, possible security issue (python/tests/kube/test_executor.py:353)

Issue: [72-codacy-function-call-with-shell-true-parameter-identified-possible-security-issue-python-tests-kube-test-executor-py.md](../../issues/72-codacy-function-call-with-shell-true-parameter-identified-possible-security-issue-python-tests-kube-test-executor-py.md)

## Overview

Codacy's Bandit scan (`Bandit_B604`) flags `python/tests/kube/test_executor.py:353` as "Function call with shell=True parameter identified, possible security issue" (Codacy issue `c97af1849d98eae18c934ff889a69d3b`).

## Context

Lines 353 and 390 of `python/tests/kube/test_executor.py` both contain `shell="bash",` — a keyword argument to the module's `_config()` test helper (`python/tests/kube/test_executor.py:12`), which only assembles a `MagicMock` config object's `.data` dict. Neither call ever reaches `subprocess.run`: both tests patch `kube.executor.exec_shell` directly via `@patch("kube.executor.exec_shell")`, so no real process is spawned. Bandit's B604 rule pattern-matches on the literal `shell=` text near a call and doesn't distinguish this from an actual `subprocess.run(..., shell=True)` invocation. The real `exec_shell` implementation (`python/kube/exec.py:37`) already uses list-form `subprocess.run` args with no `shell=True`, and already carries a `# nosec B603, B607 - fixed binary, list-form args, no shell` suppression comment — the repo's established convention for documenting why a Bandit finding doesn't apply (also used in `python/kube/auth.py`, `python/kube/scope.py`, `python/kube/inventory.py`, `python/kube/completion.py`).

Codacy only flagged line 353 in this issue, but line 390 has the byte-for-byte identical pattern and would trip the same rule — the decision (confirmed during issue discussion) is to fix both now rather than wait for a near-duplicate future Codacy finding.

## Implementation Steps

### Step 1 — Suppress the false positive at both occurrences

Add a `# nosec B604 - ...` comment to the `shell="bash",` line inside each of the two `_config(...)` calls (`test_executor.py:353` and `test_executor.py:390`), explaining that this is mock config fixture data consumed only by `mock_exec.assert_called_once_with(...)`, not a real `shell=True` subprocess call — e.g.:

```python
shell="bash",  # nosec B604 - mock config value; exec_shell is patched, no real subprocess call
```

Keep the reasoning on one line, matching the terse style already used for `# nosec` comments elsewhere in `python/kube/`. No behavioral change to the tests — `pytest` output must be identical before and after.

## Files to Change

- `python/tests/kube/test_executor.py` — add a `# nosec B604` suppression comment (with reason) to the `shell="bash",` line at 353 and at 390.

## CI Checks

- `python`: `pytest` (CI job: `tests`)
- `python`: `ruff check .` (CI job: `lint`)

## Notes

- Purely a test-file annotation; no production code (`python/kube/`) changes.
- Verify locally that `pytest` and `ruff check .` still pass after adding the comments — a misplaced `# nosec` on a multi-arg line can trip `ruff`'s line-length rule, so keep the comment short.
