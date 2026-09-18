# Issue: Codacy: subprocess call - check for execution of untrusted input (python/kube/exec.py:27)

## Description
Codacy (Bandit `B603`) flags the `subprocess.run` call in `exec_shell` (`python/kube/exec.py:27`) for executing input that isn't validated before reaching the `kubectl` argv, mirroring issue #63's finding on `inventory.py`.

## Problem
`exec_shell(namespace, pod, shell)` builds `kubectl exec -n <namespace> -it <pod> -- <shell>` and runs it via `subprocess.run` with an existing `# nosec B603, B607` suppression, but relies solely on the list-form/no-shell invocation — there is no actual guard validating `namespace` and `pod` before they're interpolated into the argv, unlike `get_pod`/`list_pods` in `inventory.py`, which now validate via `is_valid_resource_name` (added in issue #63).

## Solution
Validate `namespace` and `pod` in `exec_shell` using the existing `kube.validation.is_valid_resource_name` helper before building the `kubectl` argv, returning `(False, <error>)` on an invalid value — same pattern as `inventory.get_pod`/`list_pods`. The `shell` argument (sourced from local config, not raw user/API input) is out of scope for this validation.

## Benefits
Closes the untrusted-input gap Bandit B603 flags, keeps the suppression comment honest (an actual guard backs it, not just the invocation style), and brings `exec.py` in line with the validation already applied to `inventory.py`.
