# Plan: Codacy: Possible hardcoded password: '--namespace' (python/kube/completion.py:76)

Issue: [79-codacy-possible-hardcoded-password-namespace-python-kube-completion-py-76.md](../../issues/79-codacy-possible-hardcoded-password-namespace-python-kube-completion-py-76.md)

## Overview
Suppress the Bandit B105 false positive on `python/kube/completion.py:76`, where the flag literal `"--namespace"` is misread as a hardcoded password.

See [python.md](python.md) for the full plan.
