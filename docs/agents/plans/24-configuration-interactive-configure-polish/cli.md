# Cli Plan: Configuration: interactive configure + polish

Main plan: [plan.md](plan.md)

## Shared contracts

- `python` is adding a `--json` flag to `kube list` and turning `kube configure context|namespace|pod` from a stub into a real interactive flow (no new subcommands, no changed argument names for the commands already documented). `cli` only needs to reflect that in the registered help text — it does not touch `python/kube/` or `bin/tingle` itself, since the `kube` entry point and its subcommand names are unchanged.

## Implementation Steps

### Step 1 — Update `kube`'s registered help text

Update the `kube` entry in `commands/python.json`: add `--json` to the `list namespace`/`list pods` usage/examples lines, and change the `configure context|namespace|pod` usage lines to reflect that they now run a real interactive create/edit/remove flow instead of being unimplemented placeholders.

## Files to Change

- `commands/python.json` — update the `kube` entry's `long_help` (usage + examples) as described above.
