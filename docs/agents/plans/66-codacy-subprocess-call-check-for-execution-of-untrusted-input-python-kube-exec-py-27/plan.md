# Plan: Codacy: subprocess call - check for execution of untrusted input (python/kube/exec.py:27)

Issue: [66-codacy-subprocess-call-check-for-execution-of-untrusted-input-python-kube-exec-py-27.md](../../issues/66-codacy-subprocess-call-check-for-execution-of-untrusted-input-python-kube-exec-py-27.md)

## Overview
`exec_shell` in `python/kube/exec.py` builds a `kubectl exec` argv from `namespace` and `pod` without validating them first, which is why Bandit B603 still flags the `subprocess.run` call despite the existing `nosec` suppression. This plan closes the gap by validating `namespace` and `pod` with the existing `kube.validation.is_valid_resource_name` helper before the argv is built — the same guard already applied to `inventory.get_pod`/`list_pods` in issue #63.

See [python.md](python.md) for the full plan.
