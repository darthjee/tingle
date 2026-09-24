# Guide Plan: docs: add user guide for `tingle kube` (docs/guides/kube.md)

Main plan: [plan.md](plan.md)

## Overview

Write `docs/guides/kube.md`, an end-user guide for `tingle kube`, following
the style of `docs/guides/install.md` and `docs/guides/linux.md`, and replace
the *(guide coming soon)* placeholder in `docs/guides/README.md` with a link.

## Context

`tingle kube` (registered in `commands/python.json`, implemented under
`python/kube/`) is an EKS helper built on scoped aliases for contexts,
namespaces and pods, stored in `~/.tingle/kube/config.json`. #171 added
env-credential mode (`python/kube/auth.py`). Today the only user docs are the
dense `long_help` string.

Where `long_help` or the issue text disagree with the code, the guide
documents **the real code behaviour**:

- A **missing** config is not pass-through: kube writes `{"version": 1}` and
  prints `kube: created new config at <path>`. Only an unreadable,
  invalid-JSON or wrong-shape file triggers pass-through
  (`kube: <reason> — falling back to pass-through mode.`).
- `list pods` requires `--namespace <alias>` after `pods`; `--json` goes
  before `namespace`/`pods`: `tingle kube list [--json] pods --namespace <alias>`.

## Implementation Steps

### Step 1 — Write `docs/guides/kube.md`

Follow the existing guide conventions: H1 `` # `tingle kube` `` plus the
`short_help` sentence; untagged code fences; ~76-column prose. Suggested
outline:

1. `## What it does`
2. `## Prerequisites` — `aws`, `kubectx`, `kubectl` on `PATH`.
3. `## Usage` — one fenced block with every form (`switch <context_alias>`,
   `list [--json] namespace`, `list [--json] pods --namespace <alias>`,
   `shell <namespace_alias> <pod_alias>`, `configure context|namespace|pod`).
4. `## The config file` — path, example JSON, key table (`version` required;
   `aws_profile` default `default`; `pod_id_pattern` default
   `^[a-z0-9]{10}$`; `shell` default `bash`; `contexts`, `namespaces`,
   `pods` default `{}`), block shapes, active scope (context alias whose real
   name equals `kubectl config current-context`), pod matching (`prefix` +
   `id_pattern` / `pod_id_pattern`).
5. `## When the config is missing or invalid` — created fresh vs
   pass-through; note that `configure` cannot save while the file is broken
   (fix or delete it first).
6. `## AWS credentials` — profile mode, env mode (`AWS_ACCESS_KEY_ID` +
   `AWS_SECRET_ACCESS_KEY`, `aws_profile` ignored), partial-credentials
   warning and fallback; check runs before `switch`/`list`/`shell`, not
   `configure`.
7. `` ## `tingle kube switch` ``, `` ## `tingle kube list` ``,
   `` ## `tingle kube shell` `` — synopsis, behaviour, output shapes
   (including `--json`), pod selection prompt, notices for unknown aliases.
8. `` ## `tingle kube configure` `` — action menu, context flow, scope prompt
   for namespace/pod, pod prompts, cascading removal with confirmation,
   validation before every save (`— nothing saved.`), atomic writes; editing
   with a new alias adds rather than renames.
9. `## From kubectx/kubectl to kube` — numbered walkthrough mapping: export
   `AWS_*` -> env mode; `kubectx` -> `configure context`; `kubectx <ctx>` ->
   `switch`; `kubectl get ns` -> `list namespace`;
   `kubectl get pods -n $NAMESPACE | grep <name>` -> `list pods --namespace`;
   `kubectl exec -n $NAMESPACE -it $POD -- bash` -> `shell`.
10. `## Errors` — exact messages in fenced blocks.
11. `## Quick help` — `tingle --help kube`.

Verify every statement against `commands/python.json` and `python/kube/`
(`parser.py`, `executor.py`, `auth.py`, `constants.py`, `config.py`,
`configure.py`, `scope.py`, `matching.py`).

### Step 2 — Link the guide from `docs/guides/README.md`

Replace:

```
- `kube` — Kubernetes (EKS) subcommand with a scoped alias layer. *(guide coming soon)*
```

with:

```
- [`kube`](kube.md) — Kubernetes (EKS) subcommand with a scoped alias layer.
```

## Files to Change

- `docs/guides/kube.md` — new end-user guide.
- `docs/guides/README.md` — link the kube guide.

## CI Checks

No CI job checks docs (CircleCI runs only ruff/pytest under `python/`).
Codacy runs markdownlint (MD013 and MD040 disabled). Optional local check,
ignoring MD013/MD040 hits:

- `docs/guides/`: `npx --yes markdownlint-cli2 docs/guides/kube.md docs/guides/README.md`

## Notes

- Watch MD024 (no duplicate headings — use unique H3 names), MD036 (no
  emphasis-as-heading), MD033 (no inline HTML such as `<kbd>`), MD014 (no
  `$ ` prompts without output), MD029 (ordered list numbering).
- The `long_help` inaccuracies (missing-config wording, `list pods` usage
  without `--namespace`) are out of scope here; they belong to a follow-up
  touching `commands/python.json`.
