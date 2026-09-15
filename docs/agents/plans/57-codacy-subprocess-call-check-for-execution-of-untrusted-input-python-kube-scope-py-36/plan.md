# Plan: Codacy: subprocess call - check for execution of untrusted input (python/kube/scope.py:36)

Issue: [57-codacy-subprocess-call-check-for-execution-of-untrusted-input-python-kube-scope-py-36.md](../issues/57-codacy-subprocess-call-check-for-execution-of-untrusted-input-python-kube-scope-py-36.md)

## Overview
Codacy flags `python/kube/scope.py:36` for Bandit rule `B603` on a `subprocess.run` call. The same safe-by-construction pattern (fixed binary name, list-form args, no `shell=True`) is repeated across `python/kube/scope.py`, `auth.py`, `exec.py`, and `inventory.py`. Suppress `B603` at every one of these call sites with an inline `# nosec B603` comment documenting why it's safe, instead of fixing only the single flagged line.

See [python.md](python.md) for the full plan.
