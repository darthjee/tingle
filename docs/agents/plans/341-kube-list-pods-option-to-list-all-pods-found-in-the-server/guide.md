# Guide Plan: kube list pods: option to list all pods found in the server

Main plan: [plan.md](plan.md)

## Shared contracts

- Usage: `tingle kube list [--json] pods --namespace <namespace_alias> [--all]`.
- With `--all`: alias blocks, then an always-printed `(unmatched):` block of
  pods matched by no displayed alias (oldest first); no "candidates discarded
  by id_pattern" hint. JSON: final entry `{"alias": null, "pods": [...]}`,
  always present.
- `--all` only covers the given namespace (unlike kubectl's
  `--all-namespaces` / `-A`).

## Implementation Steps

### Step 1 — Document --all in docs/guides/kube.md

- *Usage*: add `tingle kube list pods --namespace web --all` to the examples
  block.
- *Listing pods*: add `[--all]` to the synopsis; replace "Pods that match no
  alias are not listed" with a pointer to `--all`; add a short `--all`
  subsection with a text sample (alias blocks + `(unmatched):`) and a JSON
  sample (final `"alias": null` entry), noting it is always printed, the
  discarded hint is dropped, and it is per-namespace (not kubectl's `-A`).
- *Active scope*: note that with no active scope or no aliases, `list pods
  --all` still shows every pod (under `(unmatched)`).
- *From kubectx/kubectl to kube*: mention `list pods --all` as the equivalent
  of a plain `kubectl get pods -n <namespace>`.

## Files to Change

- `docs/guides/kube.md` — sections listed above.

## Notes

- Keep wording and sample names consistent with the existing guide (e.g. the
  `api`/`worker` aliases used in *Listing pods*).
