# CLI Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Main plan: [plan.md](plan.md)

## Shared contracts

- Subcommand `tingle kube example` (no arguments), printing a step-by-step
  guide from configuration to shell.

## Implementation Steps

### Step 1 — Update kube help

In `commands/python.json`, `kube.long_help`:

- add one sentence: `example` prints a step-by-step walkthrough from
  configuring aliases to opening a shell in a pod;
- add `tingle kube example` to **Usage** and **Examples**;
- fix the existing inaccuracy: Usage shows
  `tingle kube list [--json] pods` → `tingle kube list [--json] pods
  --namespace <namespace_alias>`, and Examples' `tingle kube list --json pods`
  → `tingle kube list --json pods --namespace web` (keep the help's existing
  example names).

## Files to Change

- `commands/python.json` — `kube.long_help`.
