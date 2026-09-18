# Plan: Codacy: Starting a process with a partial executable path (python/kube/exec.py:27)

Issue: [65-codacy-starting-a-process-with-a-partial-executable-path-python-kube-exec-py-27.md](../../issues/65-codacy-starting-a-process-with-a-partial-executable-path-python-kube-exec-py-27.md)

## Overview
Codacy's B607 finding is stale — the flagged `subprocess.run` call already resolves `kubectl` via `binaries.resolve()`. This plan documents that with a comment, matching the same fix already applied to `inventory.py` in issue #59.

See [python.md](python.md) for the full plan.
