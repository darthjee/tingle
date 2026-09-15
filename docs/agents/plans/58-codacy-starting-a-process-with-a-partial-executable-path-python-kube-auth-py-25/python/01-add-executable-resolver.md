# Add a shared executable-resolution helper

Add a small module-level helper that resolves an executable name (`aws`, `kubectl`, `kubectx`) to its absolute path via `shutil.which`, falling back to the bare name when it cannot be resolved (e.g. not on `PATH`). This keeps the resolution logic in one place instead of duplicating a `shutil.which(...) or name` expression at every call site, and keeps the existing exception-free contract of the calling functions intact — an unresolved binary still reaches `subprocess.run` (and fails the same way it does today), rather than raising.

Create `python/kube/binaries.py`:

```python
"""
binaries.py — Executable path resolution for kube.

Resolves a bare executable name (e.g. "aws", "kubectl") to its absolute
path via `shutil.which`, satisfying Bandit B607 ("starting a process with
a partial executable path") for the subprocess.run call sites in auth.py,
exec.py, inventory.py, and scope.py. Falls back to the bare name when the
binary can't be resolved (e.g. not on PATH), so a missing binary still
fails the same way it does today — a normal command error, not a new
exception path.
"""

from __future__ import annotations

import shutil


def resolve(name: str) -> str:
    """Return the absolute path to `name`, or `name` unchanged if unresolved."""
    return shutil.which(name) or name
```

## Files to Change
- `python/kube/binaries.py` — new module with the `resolve(name)` helper described above.
