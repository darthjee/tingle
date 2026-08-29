# Python Plan: Execution: shell (the anchor command)

Main plan: [plan.md](plan.md)

## Steps

- [01 — Add single-pod fetch helper](python/01-add-get-pod-helper.md)
- [02 — Add interactive-exec and ambiguity-prompt helpers](python/02-add-exec-and-prompt-helpers.md)
- [03 — Implement Kube._shell](python/03-implement-shell-handler.md)

## CI Checks

- `python`: `pytest` (CI job: `tests`)
- `python`: `ruff check .` (CI job: `lint`)

## Notes

- Reuses #21's `check_aws_credentials`/`detect_active_scope` and #22's `resolve_namespace_alias`/`active_scope_pods`/`match_pods` as-is — no changes needed to those files.
- The interactive exec step (`kubectl exec ... -it`) must not use `capture_output=True`, unlike every other `subprocess.run` call in `kube/`, so its stdio is inherited by the calling terminal — this can't be asserted with a captured-output test the way the other subprocess wrappers are; mock `subprocess.run` and assert on the call arguments instead.
