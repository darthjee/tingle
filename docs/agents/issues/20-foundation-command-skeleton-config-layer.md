# Issue: Foundation: command skeleton + config layer

## Description
Foundation slice of `tingle kube`, the Kubernetes (EKS) subcommand of the `tingle` Swiss-army-knife CLI. This issue establishes the command skeleton and configuration layer that every other `tingle kube` child issue builds on: it registers `kube` in the `tingle` dispatcher, lays out the Python module structure, and reads/validates `~/.tingle/kube/config.json`. It delivers nothing that touches the cluster yet — `tingle kube` exists, responds, and knows how to read its configuration.

Part of the `tingle kube` epic (parent #19). First in a strictly serial sequence of 5 child issues (#20-#24) — this issue must land before any other `tingle kube` child starts.

## Problem
`tingle kube` currently does not exist. There is no registered `kube` subcommand, no Python module for it, and no defined configuration schema — so none of the later `tingle kube` behavior (switch, list, shell, configure) has anywhere to be built on top of.

## Expected Behavior
- `tingle kube <subcommand>` is recognized by the `tingle` dispatcher and routes into the new Python module for `switch`, `list`, `shell`, and `configure` (stub/no-op behavior beyond parsing is acceptable at this stage).
- `~/.tingle/kube/config.json` is read and validated against the schema (`version`, `aws_profile`, `pod_id_pattern`, `shell`, `contexts`, `namespaces`, `pods`); defaults are applied for `aws_profile` (`default`), `pod_id_pattern` (`^[a-z0-9]{10}$`), and `shell` (`bash`) when absent.
- A missing or invalid config file degrades gracefully to full pass-through mode, with a clear notice, instead of crashing.
- The module is organized in layers (command → alias → discovery → auth) so later children can extend it without restructuring.
- Config loading/validation/defaults/pass-through behavior is covered by unit tests under `python/tests/kube/`, matching the `python/tests/check_file_size/` precedent.

## Solution
- Register `kube` as a new entry in `commands/python.json`, following the existing `check_file_size` convention (dispatcher invokes `<path> run <args>`).
- Add a new `python/kube/` module (sibling to `python/check_file_size/`) with a `main.py` flow-verb entrypoint (`run`) mirroring `check_file_size/main.py`.
- Build a dedicated, subcommand-aware parser scoped to `python/kube/` (using `argparse` subparsers) for `switch <context_alias>`, `list namespace|pods`, `shell <namespace_alias> <pod_alias>`, and `configure context|namespace|pod` — each subcommand has a distinct argument shape. `python/common/arg_parser.py` stays as-is (flat flag lists only) and continues to serve `check_file_size`; it is not extended to support subcommands.
- Implement a config-reading layer that loads `~/.tingle/kube/config.json`, validates it against the schema, applies defaults, and falls back to pass-through mode (with a notice) on missing/invalid config.
- Add unit tests under `python/tests/kube/` covering schema validation, defaults, and pass-through behavior, matching `python/tests/check_file_size/`'s coverage style.
- No `kubectl`/`kubectx`/`aws` calls in this issue — those start in child #21 (Context).

## Out of scope
- Any actual cluster/AWS interaction (`kubectx`, `kubectl`, `aws` calls) — starts in child #21 (Context).
- Alias resolution logic beyond reading the raw config structure — scoped alias resolution is built incrementally starting in child #21.
- Interactive `configure` behavior — that's child #24.

## Shared contracts owned by this issue
- **`~/.tingle/kube/config.json` schema** — this issue owns the initial schema and defaults; child #24 closes it out. Every other child reads this schema.
- **Dispatcher invocation convention** — how `bin/tingle` calls into the `kube` Python module; every later child depends on this being stable.
- **Subcommand parser shape** — the `argparse` subparsers structure for `switch`/`list`/`shell`/`configure`; children #21-#24 extend it with their own subcommand's real logic rather than re-parsing args themselves.

## Benefits
Unblocks the rest of the `tingle kube` epic (#21-#24): once this lands, context switching, discovery, exec, and configuration all have a stable command surface, config schema, and test scaffolding to build against.
