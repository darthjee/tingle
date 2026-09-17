# Plan: Codacy: Possible hardcoded password: '--json' (python/kube/completion.py:73)

Issue: [80-codacy-possible-hardcoded-password-json-python-kube-completion-py-73.md](../../issues/80-codacy-possible-hardcoded-password-json-python-kube-completion-py-73.md)

## Overview
Suppress a Bandit `B105` false positive in `python/kube/completion.py` by adding a `# nosec B105` comment to the `--json` flag comparison, matching the same fix already applied to the sibling `--namespace` comparison under issue #79.

See [python.md](python.md) for the full plan.
