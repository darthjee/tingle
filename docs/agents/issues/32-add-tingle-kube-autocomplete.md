# Issue: Add tingle kube autocomplete

## Description

`tingle kube` currently has no shell (bash) autocomplete — subcommands, targets, flags, and configured aliases all have to be typed out in full.

The repo already has a generic completion framework in place (`completions/bash/commands.sh`, documented in `docs/agents/architecture.md`): for `tingle <cmd> <TAB>`, the hub resolves `<cmd>`'s `main.<ext>`, checks whether a sibling `completion.<ext>` exists, and if so invokes it as `completion.<ext> <raw argv...>` (via `main.<ext> complete ...`), using its stdout (space/newline-separated candidates) as `compgen -W` candidates. If no `completion.<ext>` exists, it falls back to native file/folder completion.

No command in the repo has a `completion.<ext>` file yet — `kube` is the first real consumer of this scaffolding.

## Problem

Without a `completion.<ext>` handler, `tingle kube <TAB>` falls back to native file/folder completion, which is useless for `kube`'s subcommand/alias-shaped arguments (`switch`, `list`, `shell`, `configure`, plus configured context/namespace/pod aliases). Users have to remember and type every subcommand, flag, and alias name exactly, with no discoverability of what's configured.

## Expected Behavior

Pressing `<TAB>` while typing `tingle kube ...` suggests the right candidates at every position, covering two layers:

1. **Static keywords/flags**, mirrored from `parser.py`'s subparser structure (no I/O):
   - top-level subcommands: `switch`, `list`, `shell`, `configure`
   - `list`'s targets: `namespace`, `pods`, plus the `--json` flag
   - `list pods`'s `--namespace` flag
   - `configure`'s targets: `context`, `namespace`, `pod`
2. **Dynamic alias values**, read from `~/.tingle/kube/config.json` via `KubeConfig` (reusing the existing config loader, not a new parser):
   - `switch <TAB>` → configured context aliases (`config.data["contexts"]` keys)
   - `list pods --namespace <TAB>` → configured namespace aliases for the active scope
   - `shell <TAB>` → namespace aliases for the active scope
   - `shell <namespace_alias> <TAB>` → pod aliases for the active scope, filtered to those whose config `namespace` field is `None` or matches the typed `namespace_alias` — mirroring `_list_pods`'s exact filtering (`alias_config.get("namespace") in (None, parsed["namespace"])`), so suggestions never include an alias `shell` itself would reject for that namespace

Namespace/pod aliases are nested per context in `config.json`, so scoping them correctly requires knowing the active context. Completion reuses `scope.py`'s existing `detect_active_scope()` (a cheap local `kubectl config current-context` read, not a network/AWS call) rather than unioning aliases across all contexts — this matches how `_list_pods`/`_shell` already scope the real commands' own behavior, so suggestions stay consistent with what the command would actually do.

## Solution

Add `python/kube/completion.py`, and extend `python/kube/main.py`'s flow-verb dispatcher to forward the `complete` verb to it (mirroring how it already forwards `run` to `executor.py`).

**Implementation contract to honor** (per `docs/agents/architecture.md`):
- `completion.py` receives raw argv starting at the subcommand (`main.py`'s flow-verb dispatch strips `complete` before forwarding), including a possibly-empty trailing element for the word currently being typed.
- Must **not** parse this argv with `argparse` (or another strict parser) — the trailing empty string is significant and would be rejected/dropped.
- Output: space/newline-separated candidate strings on stdout (consumed via `compgen -W`).

**Edge cases to handle:**
- Pass-through/missing config already degrades to `{}` for all keys (`config.py`'s `_fallback`) — dynamic suggestions simply disappear; static keyword completion still works. No special-casing needed.
- No active context detected (`detect_active_scope()` returns `None`) — `namespaces.get(None, {})`/`pods.get(None, {})` are empty-dict lookups, same graceful degrade.
- Prefix filtering is already handled bash-side (`compgen -W ... -- "$cur"` in `completions/bash/commands.sh`); `completion.py` returns the full candidate set for the current position, not a filtered one.
- Flags can appear before or after positional targets (`list --json namespace` vs `list namespace --json`) — `completion.py` needs its own lightweight positional scan of the raw argv, not `argparse`.
- `kubectl` unavailable/erroring during active-scope detection: `scope.py`'s `detect_active_scope()` calls `subprocess.run(..., check=False)`, which only suppresses non-zero exit codes — a missing `kubectl` binary raises `FileNotFoundError`, uncaught. Guard this defensively inside `completion.py` itself (wrap the active-scope-detection call in `try`/`except`, degrade to static-only candidates on failure) rather than fixing `scope.py`/`auth.py` at the source — keeps this issue scoped to completion only, doesn't touch real-command code paths.
- **Non-goal**: completion never calls `list_namespaces()`/`list_pods()` (live cluster/API queries) — only local `config.json` aliases plus the one local `kubectl config current-context` call for active-scope detection. Keeps every keystroke fast and side-effect-free.
- `configure context|namespace|pod` needs no further argument completion beyond its three static targets — `configure.py`'s create/edit/remove flow and alias-name entry are entirely `input()`-prompt-driven after invocation, not additional CLI argv, so there's nothing more to tab-complete there.

**Testing:** add `python/tests/kube/test_completion.py`, following the existing one-test-file-per-module convention already used for every other `kube` module (`test_scope.py`, `test_config.py`, `test_parser.py`, etc.).

## Benefits

- Faster, more discoverable `tingle kube` usage — users see their own configured aliases instead of having to remember/look them up.
- Establishes the first real `completion.<ext>` implementation in the repo, serving as a reference for other commands adopting the same completion framework later.
- No added latency risk to the real commands — completion stays read-only and local (config file + one `kubectl config current-context` call), never touching the live cluster/API.
