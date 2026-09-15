# Plan: Codacy: Starting a process with a partial executable path (python/kube/auth.py:25)

Issue: [58-codacy-starting-a-process-with-a-partial-executable-path-python-kube-auth-py-25.md](../../issues/58-codacy-starting-a-process-with-a-partial-executable-path-python-kube-auth-py-25.md)

## Overview
Resolve Bandit B607 ("Starting a process with a partial executable path") for the bare `aws`/`kubectl`/`kubectx` names passed to `subprocess.run` across `kube/auth.py`, `kube/exec.py`, `kube/inventory.py`, and `kube/scope.py`, by resolving each executable to an absolute path via `shutil.which` before the call (falling back to the bare name if unresolved).

See [python.md](python.md) for the full plan.
