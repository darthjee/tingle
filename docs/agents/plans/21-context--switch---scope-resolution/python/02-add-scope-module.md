# Add the scope/alias module

Add the first slice of the alias-resolution layer plus active-scope detection, both as reusable functions (not inlined into `executor.py`), since children #22 (Discovery) and #23 (Execution) extend this same layer with namespace/pod aliases and need active-scope detection themselves.

Cover:

- **Context alias resolution**: given the `contexts` dict from `KubeConfig.data` and a `context_alias`, return the real context name/ARN if the alias is found; otherwise pass through the literal `context_alias` unchanged, with a caller-visible notice that it wasn't found in config.
- **Switch + validate**: invoke `kubectx <real_name>` (subprocess), then call `kubectl config current-context` (subprocess) and confirm it now matches `real_name` — this is the "validate the switch succeeded" acceptance criterion.
- **List available contexts**: for the "nonexistent context" error path, a function that returns the available context names — prefer the config's own `contexts` keys/values when present, falling back to parsing `kubectl config get-contexts -o name` (or equivalent) when config has no `contexts` at all (pass-through mode).
- **Active-scope detection**: `kubectl config current-context` → reverse-lookup the result in `contexts` (value → key) → return the matching alias, or `None` if the current context isn't in `contexts` (no scope / pass-through mode). This is the reusable piece every later child depends on.

## Files to Change

- `python/kube/scope.py` (new) — functions for context alias resolution, switch+validate, listing available contexts, and active-scope detection, each wrapping the relevant `kubectx`/`kubectl` subprocess call.
- `python/tests/kube/test_scope.py` (new) — unit tests covering: alias found vs. pass-through, switch validated vs. mismatch after `kubectx`, available-contexts listing from config vs. from `kubectl` fallback, and active-scope detection (match, no-match/pass-through). Mock `subprocess.run` throughout — no real cluster/CLI calls in tests.
