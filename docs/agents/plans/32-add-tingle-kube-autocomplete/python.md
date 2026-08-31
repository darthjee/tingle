# Python Plan: Add Tingle Kube Autocomplete

Main plan: [plan.md](plan.md)

## Implementation Steps

### Step 1 — Implement `completion.py` and wire the `complete` flow verb

Add `python/kube/completion.py` exposing a single entry point (e.g. `complete(argv: list[str]) -> list[str]`) that returns the full candidate set for the current cursor position — prefix filtering against `$cur` is already done bash-side in `completions/bash/commands.sh` via `compgen -W ... -- "$cur"`, so this must not filter by prefix itself.

`argv` is the raw argv starting at the subcommand (mirroring `KubeArgParser`'s input shape), including a possibly-empty trailing element for the word currently being typed. **Do not** parse it with `argparse` — the trailing empty string is significant. Instead, do a lightweight positional scan that tolerates flags (`--json`, `--namespace <value>`) appearing before or after positional tokens, since `KubeArgParser` itself accepts both orders.

Candidate resolution by position, mirroring `KubeArgParser`'s subparser structure (`python/kube/parser.py`):

- No subcommand yet (or a partial one) → `switch`, `list`, `shell`, `configure`.
- `switch <TAB>` → configured context aliases: `KubeConfig().data.get("contexts", {})` keys.
- `list <TAB>` → `namespace`, `pods`, `--json`.
- `list pods <TAB>` (or `list --json pods <TAB>`) → `--namespace`.
- `list pods --namespace <TAB>` → configured namespace aliases for the active scope: `config.data.get("namespaces", {}).get(active_scope, {})` keys.
- `shell <TAB>` → namespace aliases for the active scope (same lookup as above).
- `shell <namespace_alias> <TAB>` → pod aliases for the active scope, filtered to those whose config `namespace` field is `None` or matches the typed `namespace_alias` — mirror `executor.py`'s `_list_pods` filtering exactly: `alias_config.get("namespace") in (None, namespace_alias)`, applied over `scope.active_scope_pods(config.data.get("pods", {}), active_scope)`.
- `configure <TAB>` → `context`, `namespace`, `pod` (no further completion beyond this — `configure.py`'s create/edit/remove flow and alias entry are `input()`-prompt-driven, not additional argv).

Active-scope detection: call `scope.detect_active_scope(config.data.get("contexts", {}))` wrapped in its own `try`/`except` inside `completion.py` — a missing `kubectl` binary raises an uncaught `FileNotFoundError` from `subprocess.run` (only non-zero exit codes are suppressed by `check=False`). On any exception, degrade to static-only candidates for that position (treat `active_scope` as `None`) rather than crashing completion. Do not fix this at the `scope.py`/`auth.py` source — keep the fix scoped to `completion.py`.

Never call `inventory.list_namespaces()`/`inventory.list_pods()` (live cluster/API queries) from `completion.py` — only `KubeConfig()` (local file) and the one local `kubectl config current-context` call inside `detect_active_scope()`. A missing/invalid config already degrades to `{}` for every key via `KubeConfig`'s pass-through fallback, so dynamic suggestions simply disappear with no special-casing needed; static keyword completion still works.

Output: print candidates space/newline-separated on stdout (consumed via `compgen -W`), not as a Python list/JSON.

Wire `python/kube/main.py`: extend the `flow` dispatch (currently only handling `"run"`) with a `"complete"` branch that calls `completion.py`'s entry point with `sys.argv[2:]` and prints the result, mirroring how `"run"` already forwards to `Kube().run(args)`.

### Step 2 — Add `test_completion.py`

Add `python/tests/kube/test_completion.py`, following the existing one-test-file-per-module convention (`test_scope.py`, `test_config.py`, `test_parser.py`, etc.), covering:

- Top-level static completion (no/partial subcommand) returns `switch`, `list`, `shell`, `configure`.
- `list <TAB>` returns `namespace`, `pods`, `--json`; `list pods <TAB>` returns `--namespace`; flags before vs. after positionals (`list --json pods` and `list pods --json`) resolve to the same position.
- Dynamic candidates: `switch <TAB>` returns configured context aliases; `list pods --namespace <TAB>` and `shell <TAB>` return namespace aliases scoped to the active context (mock `KubeConfig`/`scope.detect_active_scope`, same style as `test_executor.py`).
- `shell <namespace_alias> <TAB>` returns pod aliases filtered to `namespace is None or namespace == namespace_alias` — assert an alias configured for a *different* namespace is excluded.
- `configure <TAB>` returns `context`, `namespace`, `pod` and nothing further past that.
- Graceful degradation: pass-through config (`KubeConfig().pass_through` / empty `data`) still returns static candidates with no dynamic ones; `detect_active_scope` raising `FileNotFoundError` (missing `kubectl`) is caught and degrades to static-only, not propagated.

## Files to Change

- `python/kube/completion.py` — new completion handler (static keywords + dynamic alias candidates, positional/flag scan, defensive active-scope detection).
- `python/kube/main.py` — forward the `complete` flow verb to `completion.py`, same pattern as the existing `run` forwarding to `executor.py`.
- `python/tests/kube/test_completion.py` — new test file covering static/dynamic candidates, namespace-filtered pod aliases, and graceful degradation.

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)

## Notes

- Mirror `unittest.mock`/`MagicMock`/`patch` conventions already used in `python/tests/kube/test_scope.py` and `test_executor.py` when the next step's tests need to stub `subprocess.run`/`KubeConfig`.
- Flags can appear before or after positional targets (`list --json namespace` vs `list namespace --json`) — the positional scan must not assume flag position.
- No live cluster/API calls from completion — keeps every keystroke fast and side-effect-free (confirmed non-goal in the issue).
