# Plan: Codacy: Reimport 'KubeConfig' (imported line 5) (python/tests/kube/test_configure.py:11)

Issue: [85-codacy-reimport-kubeconfig-imported-line-5-python-tests-kube-test-configure-py-11.md](../../issues/85-codacy-reimport-kubeconfig-imported-line-5-python-tests-kube-test-configure-py-11.md)

## Overview
Remove a redundant function-local import of `KubeConfig` from the test helper `_real_config`, so the class is imported once at module level.

See [python.md](python.md) for the full plan.
