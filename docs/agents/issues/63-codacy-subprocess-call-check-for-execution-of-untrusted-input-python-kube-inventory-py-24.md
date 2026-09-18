# Issue: Codacy: subprocess call - check for execution of untrusted input (python/kube/inventory.py:24)

## Description
Codacy flags a Bandit `B603` warning ("subprocess call - check for execution of untrusted input") on the `subprocess.run` calls in `python/kube/inventory.py` (`list_namespaces`, `get_pod`, `list_pods`). These calls already carry `# nosec B603, B607` suppression comments (added in #57/#58) because they use list-form args with no shell, and the executable path is resolved via `binaries.resolve()`. Codacy re-reported the finding regardless, and on inspection the suppression only addresses the shell-injection angle — it does not address a real, unvalidated-input gap.

## Problem
`get_pod(namespace, name)` and `list_pods(namespace)` place caller-supplied `namespace`/`name` strings directly into the `kubectl` argv list (see callers in `executor.py`, which resolve these from user CLI input/aliases). Because `subprocess.run` uses list-form args (no `shell=True`), classic shell injection is not possible, but **argument injection** still is: a value beginning with `-` (e.g. a namespace or pod name of `--kubeconfig=/tmp/evil` or `--token=...`) would be passed to `kubectl` as an additional flag instead of a positional argument, since nothing validates the shape of these values before they reach the process argv. The existing `nosec` comments correctly rule out shell injection but leave this argument-injection gap open, so the finding is not a pure false positive.

## Expected Behavior
Before being placed into the `kubectl` argv list, `namespace` and pod `name` values should be validated against Kubernetes resource-name syntax (RFC 1123 label: lowercase alphanumeric and `-`, must start/end alphanumeric, bounded length). A value that does not conform should be rejected without invoking `kubectl`, returning an error tuple consistent with this module's existing "never raise" contract (`([], error)` / `(None, error)`).

## Solution
Add `python/kube/validation.py` with a function that checks a string against full RFC 1123 label rules (lowercase alphanumeric and `-`, must start/end alphanumeric, max length 63 for namespaces / 253 for names as applicable). Call it at the top of `get_pod` and `list_pods` in `inventory.py` before building the `subprocess.run` argv, short-circuiting with an error tuple on a non-conforming value. A shared module lets other `kube` modules (e.g. `scope.py`, `matching.py`) reuse the same check later. Keep the existing `# nosec B603, B607` comments in place — they remain accurate for the shell-injection/partial-path angles — and document in a comment why the new validation, not `nosec` alone, is what actually closes the untrusted-input concern.

## Benefits
- Closes an actual untrusted-input path (argument injection into `kubectl`), not just a Codacy suppression.
- Keeps `inventory.py`'s no-raise, error-tuple contract intact for invalid input.
- Gives Codacy a real code-based justification the next time it scans this file, rather than relying solely on inline suppression comments.
