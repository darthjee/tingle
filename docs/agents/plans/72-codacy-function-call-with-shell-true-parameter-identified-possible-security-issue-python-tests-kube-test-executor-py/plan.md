# Plan: Codacy: Function call with shell=True parameter identified, possible security issue (python/tests/kube/test_executor.py:353)

Issue: [72-codacy-function-call-with-shell-true-parameter-identified-possible-security-issue-python-tests-kube-test-executor-py.md](../../issues/72-codacy-function-call-with-shell-true-parameter-identified-possible-security-issue-python-tests-kube-test-executor-py.md)

## Overview

Codacy's Bandit scan (`Bandit_B604`) flags `shell="bash",` at `python/tests/kube/test_executor.py:353` as a possible `shell=True` security issue. It's a false positive — that line is a keyword argument to a mock-config test helper, never reaching a real `subprocess` call. Fix is entirely within `python/tests/kube/`.

See [python.md](python.md) for the full plan.
