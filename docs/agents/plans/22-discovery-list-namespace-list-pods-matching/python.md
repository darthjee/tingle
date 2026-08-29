# python Plan: Discovery: list namespace + list pods + matching

Main plan: [plan.md](plan.md)

## Steps

- [01 — Namespace and pod alias resolution](python/01-alias-resolution.md)
- [02 — Kubectl inventory helpers](python/02-inventory.md)
- [03 — Pod-matching pipeline](python/03-matching.md)
- [04 — Require --namespace on list pods](python/04-require-namespace-flag.md)
- [05 — Wire up list namespace / list pods handlers](python/05-list-handlers.md)

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes

- A pod alias's optional `namespace` config field (`pods[context][alias].namespace`) is intentionally not read or validated in this issue — confirmed out of scope during discussion, left for a later issue.
- `list pods` displays every real pod matching each configured alias's prefix + `id_pattern` rule, ordered deterministically (oldest `creationTimestamp` first) — it does not collapse a group down to a single pod. Collapsing to one target and prompting on real ambiguity is child #4's (`shell`'s) responsibility, reusing the pipeline built here.
- Depends on child #2 (Context) for active-scope detection (`kube.scope.detect_active_scope`) and the AWS pre-check (`kube.auth.check_aws_credentials`), both already implemented.
