# Issue: kube list pods: option to list all pods found in the server

## Description

`tingle kube list pods --namespace <alias>` fetches every pod in the namespace
from the cluster, but only prints the pods that match a configured pod alias
(prefix + `id_pattern`) for the active scope and that namespace
(`python/kube/executor.py` — `_list_pods`). Pods that match no alias are
silently dropped, so there is no way to see everything the server returned
without falling back to `kubectl get pods -n <real-namespace>`.

## Problem

Pods that match no configured alias are invisible to `tingle kube list pods`. This is most painful when there is no active scope or no pod aliases configured — the command then prints nothing at all, even though the namespace has pods.

## Expected Behavior

`tingle kube list pods --namespace <alias> --all` lists every pod returned by the server for that namespace: pods grouped under the alias(es) they match, plus a final `(unmatched)` group. Without `--all`, output (text and JSON) is unchanged.

### Output format

With `--all`, the output keeps today's per-alias blocks and appends one final
group for the pods no displayed alias matched.

Text:

```
api:
  - api-server-7d9f8c6b5d-x2k4q
worker:
(unmatched):
  - redis-0
  - worker-old-name
```

JSON — today's `[{alias, pods}]` list plus a final entry with `"alias": null`,
mirroring `list namespace --json`, which already uses `alias: null` for
unaliased names:

```json
[
  {"alias": "api", "pods": ["api-server-7d9f8c6b5d-x2k4q"]},
  {"alias": "worker", "pods": []},
  {"alias": null, "pods": ["redis-0", "worker-old-name"]}
]
```

Rules:

- The text label is `(unmatched)` (parenthesized) so it cannot collide with a
  pod alias literally named `unmatched`.
- "Unmatched" means matched by none of the aliases displayed. Aliases scoped to
  another namespace are already filtered out, so pods they would match land in
  `(unmatched)`.
- A pod matched by more than one alias (overlapping prefixes, e.g. `api-` and
  `api-admin-`) is listed under each of them, as today; `--all` does not change
  per-alias matching.
- Unmatched pods are ordered by creation time, oldest first, like matched pods.
- The `(unmatched)` group is always printed, even when empty (JSON:
  `"pods": []`), so scripts can rely on the entry being present.
- With `--all`, the "candidates discarded by id_pattern" hint is not printed:
  those pods already appear under `(unmatched)`.

### Edge cases

- **No active scope** (current kubectl context has no alias): no pod aliases
  apply, so `--all` prints only the `(unmatched)` group with every pod (JSON: a
  single `alias: null` entry). Without the flag, output stays empty as today.
- **No pod aliases configured for the scope**: same as above.
- **Namespace argument not a configured alias**: already passed through as the
  real namespace name after the "not found in configured namespaces — using it
  as-is" notice; `--all` keeps that, so `--all --namespace <real-name>` works
  without any config.
- **Empty or nonexistent namespace**: kubectl returns no pods without an
  error; every alias block and `(unmatched)` is printed empty. No special
  message.
- **kubectl failure / AWS credential pre-check failure**: unchanged — the error
  is printed and nothing is listed (no partial output).
- **Completed / Evicted / Terminating pods**: returned by kubectl, so listed by
  name like any other pod; no status filtering (consistent with names-only
  output).

## Solution

Add an opt-in `--all` flag to `tingle kube list pods` that lists every
pod returned by the server: pods grouped under the alias they match, plus an
"unmatched" group for the rest. Supported in both text and `--json` output.

### Scope

In scope:

- A new opt-in flag on `tingle kube list pods` only.
- With the flag, every pod returned for the resolved namespace is shown,
  grouped under the alias it matches, plus an "unmatched" group.
- Both text and `--json` output.
- When nothing matches an alias, or there is no active scope, all pods land in
  the "unmatched" group — the flag is still useful there.
- Output stays names-only (no status, age or other columns), like today.
- Updates to `--help`, bash completion, `docs/guides/kube.md` and the
  `examples/` walkthrough.

Out of scope:

- `tingle kube list namespace`: it already lists every namespace returned by
  the server (annotated with `alias -> name` where an alias exists), so no flag
  is needed there. Its behavior serves as the reference for consistency.
- Any change to `list pods` output without the flag (text and JSON stay as
  they are).
- Any change to how `shell` matches pods.
- Extra filters (e.g. listing only unmatched pods).

### Flag naming

- The flag is `--all`, long form only (no kube flag has a short form today).
- It belongs to the `pods` subcommand, next to `--namespace`:
  `tingle kube list pods --namespace web --all` (and
  `tingle kube list --json pods --namespace web --all`).
- Its help text must make clear it only widens the listing within the given
  namespace — e.g. "Also list pods that match no configured alias" — to avoid
  confusion with kubectl's `--all-namespaces` / `-A`.
- Rejected: `--include-unmatched` (unambiguous but long), `--unmatched`
  (reads as "only unmatched", which is out of scope).

### Docs, completion and examples

- **Completion** (`python/kube/completion.py`): offer `--all` after
  `list pods` alongside `--namespace`; don't re-offer it once typed; recognize
  it before or after positionals (like `--json`/`--namespace`) so `--namespace`
  alias completion keeps working when `--all` comes first.
- **Help**: `--all` help text on the `pods` subparser ("Also list pods that
  match no configured alias (within the given namespace)"); update the usage
  docstrings in `python/kube/parser.py` and `python/kube/executor.py` to
  `tingle kube list pods --namespace <alias> [--all]` (they feed
  `tingle --help kube`).
- **User guide** (`docs/guides/kube.md`):
  - *Usage*: add an `--all` example line.
  - *Listing pods*: explain `--all`, with text and JSON samples showing
    `(unmatched)`, and stress it is per-namespace (unlike kubectl's `-A`).
  - *Active scope*: note that `--all` is how to see pods when there is no
    active scope or no aliases.
  - *From kubectx/kubectl to kube*: mention `--all` as the equivalent of a
    plain `kubectl get pods -n …`.
- **Examples** (`examples/kube/end_to_end.txt`): add a step right after the
  existing `list pods --namespace shop` step running
  `list pods --namespace shop --all`, with sample output including an
  `(unmatched)` group.
- **Agent docs** (`docs/agents/`): update `architecture.md`/`flow.md` only if
  they describe `list pods` behavior in enough detail to go stale.

### Alternatives considered

- Always showing every pod (no flag), mirroring `list namespace`: simpler, but
  changes the default text output and the `[{alias, pods}]` JSON shape,
  breaking backward compatibility. Rejected in favor of the opt-in flag.

### Known limitations (out of scope, possible follow-ups)

Existing behaviors noticed while scoping this issue; not caused by `--all` and
not addressed here:

- In `list pods --json`, the namespace pass-through notice is printed to stdout
  before the JSON, making the output invalid JSON when the namespace argument
  is not a configured alias.
- Pod aliases are filtered by comparing their `namespace` to the namespace
  argument as typed. Passing the real namespace name instead of its alias
  excludes aliases tied to that namespace — with `--all`, their pods would show
  up under `(unmatched)`.

## Benefits

- See everything running in a namespace without leaving tingle or dropping to `kubectl get pods`.
- Spot pods that are missing a pod alias (or whose `id_pattern` no longer matches) and fix the config.
- Useful even with no active scope or no aliases configured.
