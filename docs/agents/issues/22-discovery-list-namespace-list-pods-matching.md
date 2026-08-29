# Issue: Discovery: list namespace + list pods + matching

## Description

Discovery slice of `tingle kube`: read-only visibility into the active environment — listing namespaces and pods through the alias layer — plus the prefix + `id_pattern` matching pipeline that later underpins `shell` (child #4).

Part of the `tingle kube` epic. Depends on child #2 (Context) for active-scope detection and the AWS pre-check. Strictly serial: this issue must land before child #4 (Execution) starts.

Both `kube list namespace` and `kube list pods` are currently stub handlers in `python/kube/executor.py` (`Kube._list`), printing "not yet implemented" — this issue replaces that stub with the real implementation.

## Problem

There is no way today to see what namespaces or pods exist in the active EKS context, or to translate the short aliases configured in `~/.tingle/kube/config.json` (`namespaces`, `pods`) into real Kubernetes names. Without this, users must fall back to raw `kubectl` commands, and child #4 (`shell`) has no pod-matching pipeline to resolve a pod alias down to a single real pod.

## Expected Behavior

- `tingle kube list namespace`:
  - Runs `kubectl get namespaces -o json` (through the AWS pre-check from child #2).
  - Displays the list; when aliases exist for the active scope (`namespaces[active_scope]`), shows `alias -> name`.
- `tingle kube list pods --namespace=<namespace_alias>`:
  - `--namespace` is required — omitting it is a usage error (no implicit default namespace).
  - Resolves `namespace_alias` in the active scope's `namespaces` block (or passes through the literal value, with a notice).
  - Runs `kubectl get pods -n <ns> -o json`.
  - Displays the pods with prefix highlighting/grouping: for each configured pod alias in the active scope, shows every real pod matching that alias's `prefix` + `id_pattern` rule (not collapsed to one) — the pods within each group are ordered deterministically (oldest `creationTimestamp` first), but collapsing a group down to a single target pod is child #4's (`shell`'s) job, not this issue's.
  - A pod alias's optional `namespace` config field (`pods[context][alias].namespace`) is not read or validated by this issue — it stays unused until a later issue needs it.
- Nonexistent namespace → clear error.
- Alias not found in the active scope's `namespaces`/`pods` block → pass-through with a notice, does not block.
- `tingle kube list namespace` lists namespaces and annotates known aliases in the active scope.
- `tingle kube list pods --namespace=<alias>` resolves the namespace alias (or passes through literally) and lists matching pods grouped by alias, each group's pods deterministically ordered.
- The matching pipeline correctly discards false-positive prefix matches via `id_pattern` (e.g. `my-pod-super-<id>` is excluded from the `myp` alias, per the parent issue's example table).
- When multiple real candidates remain for a given pod alias after filtering, the group is deterministically ordered (oldest `creationTimestamp` first) rather than collapsed to one — collapsing to a single pod, and prompting on real ambiguity, is child #4's responsibility.

## Solution

**Alias resolution layer (namespaces + pods)** — extends child #2's contexts-only resolution (`kube/scope.py`) with namespace and pod alias lookups, scoped per active context, reading from the `namespaces` and `pods` blocks of `~/.tingle/kube/config.json` (schema already defined in `kube/constants.py`).

**Pod-matching pipeline** — built here as a reusable piece, called into (not re-implemented) by child #4's `shell`:
1. Determine the active scope (reuses child #2's detection).
2. Resolve `namespace_alias` in the scope → real namespace name.
3. `kubectl get pods -n <ns> -o json`.
4. Filter by `prefix` (starts with).
5. Apply the ID rule: the part after the prefix must match `id_pattern` (falls back to the global `pod_id_pattern` when a pod alias has none set).
6. Final selection — deterministic ordering (by `creationTimestamp`, oldest first) when more than one candidate remains after filtering.

**Out of scope**: `shell` (interactive exec into a pod, child #4 — owns the exec + Running pre-check + real-ambiguity prompt) and interactive `configure` (child #5).

## Benefits

- Gives users read-only visibility into namespaces and pods without dropping to raw `kubectl`.
- Establishes the alias resolution and pod-matching pipeline as a single reusable implementation, so child #4 (`shell`) doesn't re-implement prefix/id-pattern matching or risk diverging behavior.
- Locks in deterministic, false-positive-safe pod matching (via `id_pattern`) before `shell` starts relying on it for exec targeting.
