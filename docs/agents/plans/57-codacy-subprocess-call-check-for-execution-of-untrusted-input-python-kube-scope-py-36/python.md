# Python Plan: Codacy: subprocess call - check for execution of untrusted input (python/kube/scope.py:36)

Main plan: [plan.md](plan.md)

## Overview
Every `subprocess.run` call in `python/kube` already uses a hardcoded binary name (`kubectx`, `kubectl`, `aws`) with list-form arguments and no `shell=True`, so there is no real shell-injection vector — Bandit's `B603` is a generic warning that fires on any `subprocess.run`/`Popen` call regardless of exploitability. Add an inline `# nosec B603` suppression comment at each call site, with a short justification, instead of only fixing the single line Codacy currently flagged.

## Context
Codacy surfaced this on `python/kube/scope.py:36` (inside `switch_context`), but the identical pattern also appears in `scope.py`'s other three `subprocess.run` calls, plus one each in `auth.py`, `exec.py`, and `inventory.py`'s three calls. All nine call sites share the same safe shape and would trip the same Bandit rule once Codacy re-scans those files, so this plan addresses the whole module in one pass.

## Implementation Steps

### Step 1 — Add `# nosec B603` suppressions across `python/kube`
For every `subprocess.run(...)` call in `python/kube/scope.py`, `auth.py`, `exec.py`, and `inventory.py`, add a `# nosec B603` comment on the line containing `subprocess.run(` (or immediately after the closing paren if the project's Bandit/Codacy config expects the comment on the same physical line as the call — verify against how Codacy parses `nosec` comments) with a short inline justification, e.g.:

```python
result = subprocess.run(  # nosec B603 - fixed binary, list-form args, no shell
    ["kubectx", real_name],
    ...
)
```

Apply this to all nine call sites:
- `scope.py:36` — `switch_context` (`kubectx`)
- `scope.py:46` — `switch_context` (`kubectl config current-context`)
- `scope.py:77` — `list_available_contexts` (`kubectl config get-contexts`)
- `scope.py:125` — `detect_active_scope` (`kubectl config current-context`)
- `auth.py:25` — `check_aws_credentials` (`aws sts get-caller-identity`)
- `exec.py:27`
- `inventory.py:24`
- `inventory.py:49`
- `inventory.py:74`

Do not change any call's behavior (arguments, `capture_output`, `text`, `check` flags) — this is a suppression-plus-documentation change only, not a refactor.

## Files to Change
- `python/kube/scope.py` — add `# nosec B603` with justification to the 4 `subprocess.run` calls
- `python/kube/auth.py` — add `# nosec B603` with justification to the 1 `subprocess.run` call
- `python/kube/exec.py` — add `# nosec B603` with justification to the 1 `subprocess.run` call
- `python/kube/inventory.py` — add `# nosec B603` with justification to the 3 `subprocess.run` calls

## CI Checks
- `python`: `ruff check .` (CI job: `lint`) — `ruff` doesn't run Bandit rules by default in this repo's config (`python/pyproject.toml` sets no `select`), so this change won't affect lint; run it anyway to confirm the added comments don't break formatting/line-length (line-length = 100).
- `python`: `pytest` (CI job: `tests`) — no behavior changes, but run to confirm nothing broke.

## Notes
- Bandit/Codacy's `nosec` comment placement and exact format should be double-checked against Codacy's own documentation for the darthjee/tingle repo before landing, since some scanners require `# nosec` on the same line as the flagged statement's opening line rather than a trailing continuation line.
- No test changes are expected since this only adds comments — confirm existing tests in `python/tests/kube/` still pass unchanged.
