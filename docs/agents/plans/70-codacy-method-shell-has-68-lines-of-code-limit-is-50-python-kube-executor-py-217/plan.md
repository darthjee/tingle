# Plan: Codacy: Method _shell has 68 lines of code (limit is 50) (python/kube/executor.py:217)

Issue: [70-codacy-method-shell-has-68-lines-of-code-limit-is-50-python-kube-executor-py-217.md](../../issues/70-codacy-method-shell-has-68-lines-of-code-limit-is-50-python-kube-executor-py-217.md)

## Overview
`Kube._shell` in `python/kube/executor.py` needs its pod-alias-resolution logic extracted into a helper method so it drops back under Codacy's 50-line threshold, without changing any observable behavior.

See [python.md](python.md) for the full plan.
