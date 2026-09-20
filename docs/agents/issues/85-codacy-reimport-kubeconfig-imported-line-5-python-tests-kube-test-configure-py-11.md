# Issue: Codacy: Reimport 'KubeConfig' (imported line 5) (python/tests/kube/test_configure.py:11)

## Description
Codacy flagged a redundant import in `python/tests/kube/test_configure.py` as one of the repository's worst code-quality findings.

- **File**: `python/tests/kube/test_configure.py:11`
- **Pattern**: `PyLintPython3_W0404` (category: CodeStyle, severity: Info)
- **Message**: Reimport 'KubeConfig' (imported line 5)
- **Codacy issue ID**: `fdab6d3fe528bfae484f2c1c3395b578`

## Problem
`KubeConfig` is already imported at module level (line 5: `from kube.config import KubeConfig`), but the `_real_config` helper re-imports it locally (line 11). The local import is redundant and triggers pylint W0404 (reimported).

## Expected Behavior
`KubeConfig` is imported exactly once in `python/tests/kube/test_configure.py`, at module level. Codacy no longer reports `PyLintPython3_W0404` for this file, and the tests keep passing unchanged.

## Solution
Remove the redundant function-local `from kube.config import KubeConfig` inside `_real_config` (line 11) and rely on the existing module-level import (line 5), which is also used at line 94. No other changes are needed.
