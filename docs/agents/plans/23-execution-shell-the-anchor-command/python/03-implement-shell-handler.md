# Implement Kube._shell

Replace the stub `Kube._shell` in `python/kube/executor.py` with the real handler, following `_switch`/`_list_pods`'s existing layering (resolve → pre-check → act → report):

1. Run the AWS pre-check (`Kube._check_aws_credentials`, already shared by `_list_namespace`/`_list_pods`).
2. Detect the active scope (`detect_active_scope`).
3. Resolve `namespace_alias` via `resolve_namespace_alias`, printing its notice if any (pass-through on miss, same as `_list_pods`).
4. Resolve `pod_alias` against `active_scope_pods(...)`:
   - **Not configured in the active scope** — pass through: use `pod_alias` literally as the real pod name, printing a notice (mirroring `resolve_context_alias`/`resolve_namespace_alias`'s wording style), and skip straight to step 6 (no matching pipeline to run).
   - **Configured** — fetch pods in the resolved namespace (`list_pods`), then run `match_pods` with the alias's `prefix`/`id_pattern` (falling back to the config's global `pod_id_pattern`, same as `_list_pods` does).
5. Handle the matching pipeline's result:
   - **Zero candidates** — print a clear error, plus suggestions: pods in the namespace listing that match the alias's `prefix` but were discarded by `id_pattern` (i.e. `name.startswith(prefix)` but the ID-pattern check failed). Return without exec'ing.
   - **Exactly one candidate** — that's the real pod name; continue to step 6.
   - **Two or more candidates** — always call the ambiguity prompt (from step 02) with the list in `match_pods`'s already-deterministic order; never auto-pick. Use the user's selection as the real pod name.
6. Pre-validate the pod phase: `get_pod(namespace, pod)` (from step 01) — if the fetch fails, print the error and return; if `status.phase != "Running"`, print a warning but still proceed (the acceptance criteria calls for a warning, not a hard block).
7. Exec interactively via `exec_shell(namespace, pod, shell)` (from step 02), with `shell` read from `config.data.get("shell", Constants.DEFAULT_SHELL)` (`DEFAULT_SHELL = "bash"` already exists in `Constants`, no change needed there).

Wire the `_shell` entry in `Kube._handlers` to pass `config` through the same way `_switch`/`_list` already do (currently `"shell": self._shell` takes no config — this needs to become a `lambda`, matching the other two).

## Files to Change

- `python/kube/executor.py` — replace the `_shell` stub with the real implementation described above; update its `_handlers` wiring to pass `config`.
- `python/tests/kube/test_executor.py` — cover: successful resolve + exec (single match), pass-through pod alias (unconfigured), zero-match error + prefix-only suggestions, ambiguity prompt on 2+ matches, non-Running warning (still proceeds), and the AWS pre-check failure short-circuit — matching the existing `_switch`/`_list_pods` test coverage style.
