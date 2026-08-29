# Python Plan: Configuration: interactive configure + polish

Main plan: [plan.md](plan.md)

## Shared contracts

- `commands/python.json`'s `kube` entry's `long_help` (owned by `cli`) must stay in sync with the `--json` flag added to `kube list` in Step 4 and with `configure` moving from a stub to a real interactive flow (Steps 2–4). Nothing else crosses the boundary — `cli` does not read or write `python/kube/` files.

## Steps

- [01 — Safe config writer](python/01-safe-config-writer.md)
- [02 — Configure context flow](python/02-configure-context-flow.md)
- [03 — Configure namespace and pod flows](python/03-configure-namespace-pod-flows.md)
- [04 — Wire configure dispatch and --json list output](python/04-wire-dispatch-and-json-output.md)
- [05 — Section 6 edge-case sweep](python/05-edge-case-sweep.md)
- [06 — Tests](python/06-tests.md)

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes

- `KubeConfig` currently exposes only the defaults-applied `data` dict. The interactive flow must edit and persist the **raw** (pre-default) structure, or every save would bake `aws_profile`/`pod_id_pattern`/`shell` defaults into the file even when the user never set them — Step 1 covers exposing the raw dict alongside the existing defaulted one.
- Regex syntax for a pod's `id_pattern` should be validated (`re.compile`) before it's accepted in the prompt flow (Step 3) — an unparsable pattern would otherwise pass the structural schema check in `_validate_pods` (which only checks required keys) and silently corrupt matching later.
