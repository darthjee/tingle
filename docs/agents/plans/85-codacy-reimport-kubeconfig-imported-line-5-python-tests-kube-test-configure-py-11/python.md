# Python Plan: Codacy: Reimport 'KubeConfig' (imported line 5) (python/tests/kube/test_configure.py:11)

Main plan: [plan.md](plan.md)

## Overview
`python/tests/kube/test_configure.py` imports `KubeConfig` at module level (line 5) and again inside `_real_config` (line 11), which Codacy flags as pylint W0404 (reimported). Remove the local import.

## Context
The module-level import is still needed: `KubeConfig` is used in `_real_config` (line 14) and directly at line 94. Dropping the local import changes no behavior.

## Implementation Steps

### Step 1 — Remove the redundant local import
Delete `from kube.config import KubeConfig` (and the blank line after it) from the body of `_real_config`, leaving the module-level import as the only one.

### Step 2 — Verify
Run the linter and the test module to confirm nothing else depended on the local import and that no new findings appear.

## Files to Change
- `python/tests/kube/test_configure.py` — remove the function-local `KubeConfig` import in `_real_config`

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- No production code changes; test-only cleanup.
