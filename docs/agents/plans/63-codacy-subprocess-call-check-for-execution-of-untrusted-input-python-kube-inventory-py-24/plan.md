# Plan: Codacy: subprocess call - check for execution of untrusted input (python/kube/inventory.py:24)

Issue: [63-codacy-subprocess-call-check-for-execution-of-untrusted-input-python-kube-inventory-py-24.md](../issues/63-codacy-subprocess-call-check-for-execution-of-untrusted-input-python-kube-inventory-py-24.md)

## Overview
Close the untrusted-input gap behind Codacy's Bandit B603 finding on `python/kube/inventory.py`: `namespace`/pod `name` values reach `kubectl`'s argv unvalidated, which the existing `# nosec` suppressions don't actually address (they only rule out shell injection, not argument injection). Add Kubernetes name validation and wire it into `inventory.py`.

See [python.md](python.md) for the full plan.
