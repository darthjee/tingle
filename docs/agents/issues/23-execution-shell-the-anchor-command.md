# Issue: Execution: shell (the anchor command)

## Description

Execution slice of `tingle kube`: the anchor command that collapses the manual `kubectx -> get ns -> get pods -> exec` sequence into a single `tingle kube shell <namespace_alias> <pod_alias>` invocation, safely.

Part of the `tingle kube` epic (parent #19). Fourth in the strictly serial sequence of 5 child issues (#20-#24) — depends on #21 (Context) for active-scope detection and the AWS pre-check, and on #22 (Discovery) for the alias resolution + pod-matching pipeline. This issue must land before #24 (Configuration) starts.

`kube shell` is currently a stub handler in `python/kube/executor.py` (`Kube._shell`), printing "not yet implemented" — this issue replaces that stub with the real implementation.

## Problem

There is no way today to open a shell into a pod through the alias layer. Users must fall back to the manual `kubectx -> kubectl get ns -> kubectl get pods -> kubectl exec` sequence themselves, with no protection against dropping silently into a crashing/non-Running pod and no handling for genuine ambiguity when a pod alias matches more than one real pod.

## Expected Behavior

- `tingle kube shell <namespace_alias> <pod_alias>`:
  - Runs the AWS pre-check (#21 check_aws_credentials) before touching the cluster.
  - Resolves `namespace_alias` in the active scope (reusing #22 resolve_namespace_alias) — passes through the literal value with a notice if not found, same as `list pods`.
  - Resolves `pod_alias` against the active scope's `pods` block:
    - If `pod_alias` isn't configured in the active scope, passes through: the typed value is used directly as the real pod name, with a notice, skipping the matching pipeline entirely (same pass-through pattern as `resolve_context_alias`/`resolve_namespace_alias`).
    - If configured, runs it through #22's matching pipeline (match_pods) to collapse it to a single real pod.
  - Zero matches after filtering: prints a clear error, plus suggestions listing pods that match the alias's `prefix` but were discarded by `id_pattern` (per the parent epic's section 6 behavior).
  - Real ambiguity: if the matching pipeline yields more than one candidate for `pod_alias`, always lists the options and prompts the user to choose — never auto-picks the oldest silently. The pipeline's deterministic ordering (#22) only controls the order candidates are listed in the prompt.
  - Pre-validates the pod phase via `kubectl get pod -n <ns> <pod> -o json` — if not Running, prints a warning before proceeding with the exec (never drops into a CrashLoopBackOff pod silently).
  - Execs interactively: `kubectl exec -n <ns> -it <pod> -- <shell>`, where `<shell>` comes from config (`shell` key, default `bash`), inheriting the current terminal's stdio (not capture_output, unlike every other kube subprocess call so far).
- A non-Running pod triggers a warning before the exec attempt proceeds (not a silent connection).
- The configured `shell` (default `bash`) is used for the exec command.
- Any 2+ candidates surviving the matching pipeline always surfaces a choice prompt — never an automatic pick, regardless of ordering.
- Zero surviving candidates surfaces an error with prefix-only-match suggestions, not a bare failure.
- An unconfigured `pod_alias` passes through as a literal pod name, with a notice, consistent with namespace/context alias handling.

## Solution

Implement `Kube._shell` in `python/kube/executor.py` (replacing the current stub), following the same layering `_switch`/`_list` already use:

- Reuse #21's check_aws_credentials, detect_active_scope.
- Reuse #22's resolve_namespace_alias, active_scope_pods, match_pods.
- Add a single-pod fetch helper to `kube/inventory.py` (e.g. get_pod(namespace, name) wrapping `kubectl get pod -n <ns> <pod> -o json`) — no such helper exists yet; list_pods only fetches the whole namespace.
- Add an interactive-exec helper (e.g. in `kube/scope.py` or a new `kube/exec.py`) wrapping `kubectl exec -n <ns> -it <pod> -- <shell>` without capture_output=True, so the child process's stdio is inherited by the terminal.
- Add a choice-prompt helper for the real-ambiguity case (always triggered on 2+ surviving candidates, listed in #22's deterministic order; list candidates, read a selection).
- Zero-candidate path: error message plus suggestions of pods matching only the alias's `prefix` (i.e. discarded solely by `id_pattern`).
- Unconfigured `pod_alias`: pass through the literal value as the real pod name (with a notice), skipping the matching pipeline, mirroring `resolve_context_alias`/`resolve_namespace_alias`.

Out of scope: the matching pipeline itself (already built in #22; this issue only consumes it) and interactive `configure` (#24).

Add unit tests under `python/tests/kube/` covering: successful resolve+exec, non-Running warning, pass-through namespace/pod aliases, zero-match error+suggestions, and the real-ambiguity prompt path, matching the existing test_scope.py/test_matching.py coverage style.

## Benefits

- Collapses a 4-step manual kubectl/kubectx sequence into a single safe command.
- Never drops a user into a non-Running pod, or into the wrong pod on genuine ambiguity, without an explicit signal.
- Completes the anchor command of the `tingle kube` epic, unblocking #24 (Configuration), the last child in the serial sequence.
