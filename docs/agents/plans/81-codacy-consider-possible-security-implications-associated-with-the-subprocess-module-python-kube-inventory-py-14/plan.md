# Plan: Codacy: Consider possible security implications associated with the subprocess module. (python/kube/inventory.py:14)

Issue: [81-codacy-consider-possible-security-implications-associated-with-the-subprocess-module-python-kube-inventory-py-14.md](../issues/81-codacy-consider-possible-security-implications-associated-with-the-subprocess-module-python-kube-inventory-py-14.md)

## Overview
Suppress Bandit's `B404` "consider possible security implications associated with the subprocess module" finding, raised on the bare `import subprocess` line in all four `python/kube` files that import it. Batches the fix across this issue's three live siblings (#76, #82, #83) in one PR, matching the precedent set by issues #57/#58.

See [python.md](python.md) for the full plan.
