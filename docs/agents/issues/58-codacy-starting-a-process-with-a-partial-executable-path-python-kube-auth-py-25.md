# Issue: Codacy: Starting a process with a partial executable path (python/kube/auth.py:25)

## Description
Codacy flagged `python/kube/auth.py:25` for Bandit rule B607 ("Starting a process with a partial executable path"): the call to `subprocess.run(["aws", "sts", "get-caller-identity", ...])` references the `aws` binary by bare name rather than an absolute path, so PATH manipulation could point it at a different executable.

## Problem
The same partial-executable-path pattern (bare `aws`/`kubectl` in a list-form `subprocess.run` call) also exists in `python/kube/exec.py`, `python/kube/inventory.py`, and `python/kube/scope.py`, each already suppressing Bandit B603 ("subprocess call") with an inline `# nosec B603` comment and a "fixed binary, list-form args, no shell" justification, but none of them (including `auth.py`) currently addresses B607. Codacy has so far only reported the finding for `auth.py:25`, but the same risk applies everywhere the pattern is used.

## Solution
In all four files, resolve the executable (`aws` in `auth.py`; `kubectl` in `exec.py`, `inventory.py`, and `scope.py`) to its absolute path via `shutil.which(...)` before passing it to `subprocess.run`, rather than suppressing the warning with a `nosec` comment. Fall back to the bare name (preserving current behavior) if `shutil.which` cannot resolve it, so a missing binary still surfaces as a normal command failure instead of a new error path. Update the Codacy finding once resolved.

## Benefits
Removes the flagged security warning from the Codacy dashboard and closes the gap between the repo's stated "fixed binary, list-form args, no shell" trust model and what Bandit actually checks for, consistently across all four call sites rather than just the one Codacy happened to flag.
