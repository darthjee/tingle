# Issue: Context: switch + scope resolution

## Description

Context slice of `tingle kube`: switching the active Kubernetes context via a scoped alias, with the guarantee that AWS credentials are valid before any cluster operation. This is the first command that actually touches the cluster CLIs (`kubectl`, `kubectx`, `aws`).

Part of the `tingle kube` epic (parent #19). Second in a strictly serial sequence of 5 child issues (#20-#24) — depends on child #20 (Foundation), already merged. This issue must land before child #22 (Discovery) starts.

## Problem

`tingle kube` has a command skeleton and config layer (#20), but `switch` is still a stub — there is no way to actually switch the active Kubernetes context, no AWS credential pre-check, and no active-scope detection. Without these, none of the later `tingle kube` behavior (discovery, shell, configure) has a way to know which cluster/alias scope it's operating in.

## Expected Behavior

- `tingle kube switch <context_alias>` resolves the alias against `contexts` in `~/.tingle/kube/config.json` (or passes through the literal value with a notice if not found) and switches context via `kubectx <real_name>`.
- The switch is validated against `kubectl config current-context` after invocation.
- A nonexistent context alias/name produces a clear error listing the available contexts (from config, or from `kubectx` output) as a suggestion, rather than a bare failure.
- `aws sts get-caller-identity --profile <aws_profile>` runs and blocks the switch on failure, before the `kubectx` call.
- Active-scope detection (`kubectl config current-context` → reverse lookup in `contexts` → `context_alias`) is implemented as a reusable function in the alias layer, not inlined only in `switch`. If the active context has no alias, there is no scope (pass-through mode).

## Solution

- Implement `Kube._switch` in `python/kube/executor.py` (replacing the current stub):
  - Resolve `context_alias` against `contexts` in the loaded `KubeConfig` (pass through the literal value with a notice if not found).
  - Run the AWS pre-check before touching the cluster; abort with a clear message on failure.
  - Invoke `kubectx <real_name>` to switch, then validate via `kubectl config current-context`.
  - On an unresolvable context, list the available contexts as a suggestion instead of a bare failure.
- Add the AWS pre-check (`aws sts get-caller-identity --profile <aws_profile>`) as a standalone, reusable function — not wired into `executor.run()` for every subcommand. This issue calls it only from `switch`; children #22 (Discovery) and #23 (Execution) call it themselves once they add real cluster calls. `list`/`shell`/`configure` stay no-op stubs, unaffected by this issue.
- Add active-scope detection (`kubectl config current-context` → reverse lookup in `contexts` → alias) as a reusable function in the alias layer, so children #22-#23 can consume it without reimplementing.
- Add unit tests under `python/tests/kube/` covering alias resolution, pass-through, the AWS pre-check, and active-scope detection, matching the existing `test_config.py`/`test_parser.py` coverage style.

## Out of scope

- `list namespace` / `list pods` and the pod-matching pipeline — child #22 (Discovery).
- `shell` (exec into a pod) — child #23 (Execution).
- Namespace/pod alias resolution — introduced in children #22 and #23 respectively; this issue only resolves context aliases.
- Wiring the AWS pre-check into `list`/`shell`/`configure` — each of those children wires it in themselves when they add real cluster calls.

## Shared contracts owned by this issue

- **Active-scope detection** — the `kubectl config current-context` → `context_alias` mapping, exposed as a reusable function. Every later child (list namespace, list pods, shell) needs it before resolving namespace/pod aliases.
- **AWS pre-check** — the `aws sts get-caller-identity` validation gate, exposed as a reusable function for later children to call before their own cluster-touching commands.
- **Alias resolution layer (contexts)** — the first slice of the alias-resolution layer that children #22 and #23 extend with namespaces and pods.

## Benefits

Unblocks context-dependent behavior across the rest of the `tingle kube` epic: once this lands, discovery, shell, and configuration all have a validated active cluster context, a reusable AWS credential gate, and the first slice of the alias-resolution layer to build on — without any of them needing to reinvent scope detection or credential checking.
