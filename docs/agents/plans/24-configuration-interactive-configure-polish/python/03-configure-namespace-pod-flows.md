# Configure namespace and pod flows

Add `configure_namespace` and `configure_pod` to `kube/configure.py` (from Step 2). Both live inside a context block, so both cascade: scope (context alias) → action (create/edit/remove) → alias → value(s).

## `configure_namespace`

1. List configured context aliases (`config.raw.get("contexts", {})`); if there are none, print a notice that a context alias must exist first and abort (nothing to scope namespaces under).
2. Prompt to pick the scope (context alias) from that list.
3. Within that scope, list existing namespace aliases (`namespaces[scope]`), then the same create/edit/remove menu as `configure_context`.
4. **Create/edit** — prompt for alias + real namespace name, write into `namespaces[scope][alias]`.
5. **Remove** — prompt for which alias, remove it. No further cascade needed here — pods reference namespace aliases by name (a string), not by object identity, so a pod entry pointing at a since-removed namespace alias simply falls back to pass-through behavior at resolution time (existing `resolve_namespace_alias` behavior, unchanged by this issue).
6. Validate and save via `config.save(draft)` (Step 1), same abort-on-error behavior as `configure_context`.

## `configure_pod`

Same scope-first shape as `configure_namespace`, plus pod-specific fields:

1. Pick the scope (context alias), same "no contexts configured yet" guard.
2. List existing pod aliases in that scope (`pods[scope]`), then create/edit/remove menu.
3. **Create/edit** — prompt for:
   - alias
   - `prefix` (required)
   - `id_pattern` (optional; validate with `re.compile()` before accepting — reprompt on an invalid pattern rather than saving one that would break `matching.py` later)
   - `namespace` (optional; offer the scope's configured namespace aliases as a pick-list, but accept free text too since it's an alias reference, not a hard foreign key)
   Write into `pods[scope][alias]`, omitting `id_pattern`/`namespace` keys entirely when left blank (matches `POD_OPTIONAL_FIELDS` semantics — absent, not empty-string).
4. **Remove** — prompt for which alias, remove it.
5. Validate and save via `config.save(draft)`, same abort-on-error behavior.

## Files to Change

- `python/kube/configure.py` — add `configure_namespace(config: KubeConfig) -> None` and `configure_pod(config: KubeConfig) -> None`, reusing the menu/alias-picker helpers from Step 2.
