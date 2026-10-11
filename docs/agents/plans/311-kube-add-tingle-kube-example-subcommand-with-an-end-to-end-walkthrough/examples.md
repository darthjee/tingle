# Examples Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Main plan: [plan.md](plan.md)

## Shared contracts

- Produce `examples/kube/end_to_end.txt`: plain ASCII, lines <= ~80 columns,
  printed verbatim by `tingle kube example`.
- Use only the fictional setup listed in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Write the end-to-end walkthrough

Create `examples/kube/end_to_end.txt` following the issue's "Example content"
section: a title, the setup table (`demo` / `shop` / `api`), then numbered
steps:

0. Before you start (2–3 lines: `aws`, `kubectx`, `kubectl` on `PATH`; EKS
   context in kubeconfig via `aws eks update-kubeconfig ...`; credentials
   exported as `export AWS_ACCESS_KEY_ID=...` or an `aws_profile` — no values).
1. `tingle kube configure context` — prompt answers inline; hint that the real
   ARN must match `kubectl config current-context` exactly.
2. `tingle kube configure namespace` — pick `demo`, create `shop` ->
   `shop-backend`.
3. `tingle kube configure pod` — pick `demo`, create `api` (prefix
   `shop-api-`, explicit `id_pattern` with a one-line reason, namespace
   `shop`); then show the resulting `~/.tingle/kube/config.json` once.
4. `tingle kube switch demo`
5. `tingle kube list namespace`
6. `tingle kube list pods --namespace shop`
7. `tingle kube shell shop api`

Each step: one-line purpose, the command, a short excerpt of expected output.
Prompts and messages must match the real ones in `python/kube/configure.py`
and `python/kube/executor.py` (e.g. `Select an action:`, `kube switch: now
using context 'demo' (...)`). No troubleshooting section, no real
identifiers, no secrets.

## Files to Change

- `examples/kube/end_to_end.txt` — new file, the walkthrough.

## Notes

- Depends on #312 (creates the `examples` agent). If #312 is not merged yet,
  the architect writes this file following the same conventions.
- Verify ASCII: `LC_ALL=C grep -n '[^ -~]' examples/kube/end_to_end.txt`
  must print nothing; verify width with `awk 'length > 80' ...`.
