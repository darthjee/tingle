# Issue: Codacy: subprocess call - check for execution of untrusted input (python/kube/scope.py:36)

## Description
Codacy flags `python/kube/scope.py:36` for Bandit rule `B603` ("subprocess call - check for execution of untrusted input"). The same `subprocess.run(...)` pattern — a fixed, literal command name (`kubectx`, `kubectl`, `aws`) followed by list-form arguments, never `shell=True` — is repeated across the whole `python/kube` module: `scope.py` (4 call sites: `switch_context`, `list_available_contexts`, `detect_active_scope`, plus the nested `current-context` check inside `switch_context`), `auth.py` (`check_aws_credentials`), `exec.py`, and `inventory.py`. Codacy currently only surfaced the `scope.py:36` instance, but the identical pattern elsewhere would trip the same Bandit rule if/when Codacy re-scans those files.

## Problem
`B603` is a generic Bandit warning raised for any `subprocess.run`/`subprocess.Popen` call, regardless of whether the invocation is actually exploitable. In this codebase the risk is not real: every call passes a hardcoded binary name and list-form arguments (no `shell=True`, no string concatenation), so there is no shell-injection vector — at worst a resolved alias/profile string (already user-supplied CLI input, not attacker-controlled) is passed as one argv element to a fixed binary. Left unaddressed, this shows up as a recurring "worst code-quality finding" in Codacy for a pattern that is safe by construction.

## Expected Behavior
Codacy no longer flags these `subprocess.run` call sites as a security warning, and the suppression documents why each is safe (list-form args, fixed binary, no shell) so a future reviewer does not need to re-derive that judgment.

## Solution
Suppress Bandit rule `B603` at each affected `subprocess.run` call site across `python/kube/scope.py`, `auth.py`, `exec.py`, and `inventory.py`, using a `# nosec B603` comment (or the Codacy-equivalent inline ignore) with a short justification inline (e.g. `# nosec B603 - fixed binary, list-form args, no shell`). Scope is the whole module's subprocess calls, not just the single line Codacy happened to flag, since they all share the same shape and would otherwise be flagged one-by-one over time.

## Benefits
- Clears the current Codacy security finding and pre-empts the same finding from recurring on the other, currently-unflagged call sites.
- Documents in-code why the pattern is safe, instead of leaving future reviewers (or Codacy) to re-litigate it per file.
