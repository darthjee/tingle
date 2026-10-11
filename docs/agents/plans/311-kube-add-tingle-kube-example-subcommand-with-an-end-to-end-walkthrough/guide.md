# Guide Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Main plan: [plan.md](plan.md)

## Shared contracts

- `tingle kube example` prints the bundled walkthrough; no arguments; no
  config, AWS or cluster access.

## Implementation Steps

### Step 1 — Point the kube guide at the example

In `docs/guides/kube.md`:

- add `tingle kube example` to the **Usage** block and to **Examples**;
- add a short "Step-by-step example" note near the top (after "What it
  does") saying `tingle kube example` prints a complete walkthrough from
  configuration to shell, works without any config or AWS credentials, and can
  be paged with `tingle kube example | less`.

Do not copy the walkthrough itself into the guide.

## Files to Change

- `docs/guides/kube.md` — usage, examples, pointer note.
