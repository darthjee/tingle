# Wire up list namespace / list pods handlers

Replace the stub `Kube._list` in `kube/executor.py` (the one printing "not yet implemented") with real `_list_namespace` and `_list_pods` handlers, following the same static-method + AWS-pre-check pattern as `_switch`.

- Both handlers: run the AWS pre-check via `check_aws_credentials(config.data.get("aws_profile", ...))` first (same abort-and-print-message behavior as `_switch` on failure), then `detect_active_scope(config.data.get("contexts", {}))` to get `active_scope`.
- `_list_namespace(parsed, config)`:
  - `kube.inventory.list_namespaces()`; print the returned error and return if any.
  - For each namespace, look up its alias by reverse-lookup into `config.data.get("namespaces", {}).get(active_scope, {})` (build the reverse map once); print `alias -> name` when found, else just `name`.
- `_list_pods(parsed, config)`:
  - Resolve `parsed["namespace"]` via `scope.resolve_namespace_alias(config.data.get("namespaces", {}), active_scope, parsed["namespace"])`; print the notice if any.
  - `kube.inventory.list_pods(real_namespace)`; print the returned error (the "nonexistent namespace → clear error" path) and return if any.
  - `scope.active_scope_pods(config.data.get("pods", {}), active_scope)` for the configured pod aliases in scope; for each alias, call `matching.match_pods(pods, alias_config["prefix"], alias_config.get("id_pattern"), config.data.get("pod_id_pattern", Constants.DEFAULT_POD_ID_PATTERN))` and print the alias as a group heading followed by its matched pod names in the returned (already deterministic) order.
  - Pods not matched by any configured alias are not part of this issue's grouping/output — no acceptance criterion asks for an "unmatched" catch-all group.
- Update `Kube._handlers` to route `list_target == "namespace"` to `_list_namespace` and `"pods"` to `_list_pods` (replacing the single generic `_list` mapping); `list` dispatch in `_handlers` currently ignores `list_target`, so this needs its own small dispatch on `parsed["list_target"]` inside a thin `_list(parsed, config)` that delegates, mirroring how `_switch`/`_configure` already take `config`/`parsed`.

## Files to Change

- `python/kube/executor.py` — replace stub `_list` with `_list_namespace`, `_list_pods`, and a small dispatching `_list`; update imports (`kube.inventory`, `kube.matching`, `resolve_namespace_alias`, `active_scope_pods`, `detect_active_scope`).
- `python/tests/kube/test_executor.py` — new tests mirroring the `_switch` test shape: AWS pre-check failure aborts both handlers; `_list_namespace` prints `alias -> name` for known aliases and bare names for unaliased ones; `_list_pods` prints the namespace-alias notice on pass-through, the inventory error on nonexistent namespace, and groups matched pods per configured pod alias in deterministic order (including the `my-pod-super-<id>`-excluded-from-`myp` case end-to-end).
