# Namespace and pod alias resolution

Extend `kube/scope.py` with namespace and pod alias lookups, scoped per active context, mirroring the existing `resolve_context_alias` shape: given the config's `namespaces` and `pods` dicts (each keyed by context alias, per `kube/constants.py`'s schema) and the active scope alias, resolve a `namespace_alias` to its real name, and expose the active scope's configured pod aliases for the matching pipeline.

- `resolve_namespace_alias(namespaces: dict, active_scope: str | None, namespace_alias: str) -> tuple[str, str | None]`: looks up `namespaces.get(active_scope, {})`, returns `(real_name, None)` on hit, or `(namespace_alias, notice)` pass-through on miss (same shape/wording style as `resolve_context_alias`).
- `active_scope_pods(pods: dict, active_scope: str | None) -> dict`: returns `pods.get(active_scope, {})` — the pod alias config entries (`{alias: {prefix, id_pattern, namespace}}`) for the active scope, or `{}` when there is no active scope or none configured. Used by later steps to drive the matching pipeline's per-alias grouping.

Do not read or validate the optional `namespace` field on a pod alias entry — out of scope for this issue.

## Files to Change

- `python/kube/scope.py` — add `resolve_namespace_alias` and `active_scope_pods`.
- `python/tests/kube/test_scope.py` — unit tests: alias found vs. not found (with notice) for `resolve_namespace_alias`; empty/missing active scope and populated scope for `active_scope_pods`.
