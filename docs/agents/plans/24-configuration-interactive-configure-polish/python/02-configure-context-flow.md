# Configure context flow

Implement the interactive `configure context` flow in a new `kube/configure.py` module. `configure context` has no outer scope (it defines scope), so its prompts go straight to action → alias → value, unlike `namespace`/`pod` (see next step).

Flow:
1. List existing context aliases (from `config.raw.get("contexts", {})`) with their real names/ARNs, or note there are none yet.
2. Prompt for an action: create, edit, or remove (reuse `input()`-based prompting in the style of `exec.prompt_pod_choice` — numbered menu, reprompt on invalid input, empty input aborts without saving).
3. **Create/edit** — prompt for the alias (existing name pre-filled as the default on edit) and the real context name/ARN, write it into `contexts[alias]`.
4. **Remove** — prompt for which existing alias to remove, then cascade-delete: also drop `namespaces[alias]` and `pods[alias]` if present, so no orphaned scope data survives (per issue's accepted cascade-delete decision). Confirm before removing when the alias has nested namespace/pod data, listing what will be dropped.
5. After building the draft dict, call `config.save(draft)` (from Step 1). On a validation error, print it and abort without writing; on success, print a confirmation naming what changed.

## Files to Change

- `python/kube/configure.py` — new module; add `configure_context(config: KubeConfig) -> None` plus any small private helpers it needs (menu prompt, alias picker). Keep it dependency-free of `namespace`/`pod` flows (Step 3) beyond shared helpers.
