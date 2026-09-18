# Plan: Codacy: Method _list_pods has 59 lines of code (limit is 50) (python/kube/executor.py:148)

Issue: [62-codacy-method-list-pods-has-59-lines-of-code-limit-is-50-python-kube-executor-py-148.md](../issues/62-codacy-method-list-pods-has-59-lines-of-code-limit-is-50-python-kube-executor-py-148.md)

## Overview
`Kube._list_pods` in `python/kube/executor.py` exceeds the 50-line Lizard complexity limit. The fix extracts the per-alias pod-matching/"discarded by id_pattern" lookup logic (duplicated between `_list_pods` and `_shell`) into shared static helpers, and extracts `_list_pods`'s JSON/text output building into their own helpers, with no behavior change.

See [python.md](python.md) for the full plan.
