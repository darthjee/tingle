# Issue: Codacy: Method _shell has 68 lines of code (limit is 50) (python/kube/executor.py:217)

## Description
Codacy flagged `Kube._shell` in `python/kube/executor.py:217` for exceeding the method-length limit checked by the `Lizard_nloc-medium` pattern (category: Complexity, severity: Warning): the method has 68 lines of code against a limit of 50.

Codacy issue ID: `a565f771eea70f6f920c68e61e6cdf1f`.

## Problem
`_shell` (handling `kube shell <namespace_alias> <pod_alias>`) currently does all of the following in one method:

- runs the AWS credentials pre-check
- detects the active scope and resolves the namespace alias
- resolves the pod alias: falls back to using it as-is when not configured, otherwise matches candidate pods and prompts the user when more than one matches
- fetches the resolved pod and checks its running phase
- execs the shell into the pod

That is more responsibility than a single method should hold, which is why it exceeds Codacy's 50-line threshold. This is the same file where `_list_pods` was already split in issue #62 (PR #96) — `_shell` calls the `_match_pods_for_alias` helper extracted there, but its own body was left unsplit and has since grown past the limit.

## Solution
Extract the pod-alias-resolution block of `_shell` (the part that decides the real pod name — the "not configured, use as-is" fallback plus the match/prompt-if-multiple flow) into a dedicated helper method, following the same pattern already used for `_pods_json_payload`/`_print_pods_text` in issue #62. `_shell` should end up as a short orchestrator that calls the new helper, then fetches the pod, checks its phase, and execs the shell. Behavior and all existing output messages must stay unchanged.

## Benefits
- Brings `_shell` back under Codacy's line-count threshold.
- Keeps the pod-resolution logic testable in isolation, consistent with the rest of `executor.py`.
