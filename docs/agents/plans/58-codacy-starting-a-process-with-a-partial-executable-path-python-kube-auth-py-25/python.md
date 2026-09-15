# Python Plan: Codacy: Starting a process with a partial executable path (python/kube/auth.py:25)

Main plan: [plan.md](plan.md)

## Overview
Codacy flagged Bandit B607 on `kube/auth.py:25`'s bare `"aws"` executable name. The same pattern (bare `kubectl`/`kubectx` names) exists in `kube/exec.py`, `kube/inventory.py`, and `kube/scope.py`. Add a small shared helper that resolves an executable name to its absolute path via `shutil.which`, falling back to the bare name (so a missing binary still fails the same way it does today, as a normal command error rather than a new exception path), and use it at every `subprocess.run` call site across the four files. Update each file's existing `# nosec B603` comments and tests accordingly.

## Context
- All four files already suppress Bandit B603 ("subprocess call") with `# nosec B603 - fixed binary, list-form args, no shell"`, but none address B607.
- Existing tests assert the exact argument list passed to `subprocess.run` (e.g. `test_auth.py::test_passes_correct_profile_through` asserts `["aws", "sts", "get-caller-identity", ...]`), so those assertions need to expect the resolved path instead of (or alongside) the bare name.

## Steps

- [01 — Add a shared executable-resolution helper](python/01-add-executable-resolver.md)
- [02 — Use the resolver at every subprocess.run call site](python/02-apply-resolver-to-call-sites.md)
- [03 — Update tests for the new resolution behavior](python/03-update-tests.md)

## CI Checks
- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes
- `shutil.which` returning `None` (binary not on PATH) must fall back to the bare name — do not raise or change the caller-visible `(success, error)` / exception-free contract these functions already have.
- Codacy's finding is tied to `auth.py:25`; once fixed there (and consistently elsewhere), the finding should clear on the next Codacy analysis — no separate action needed beyond the code change.
