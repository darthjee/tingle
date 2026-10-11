# Product Owner Plan: kube: add `tingle kube example` subcommand with an end-to-end walkthrough

Main plan: [plan.md](plan.md)

## Shared contracts

- New top-level `examples/` folder, layout `examples/<command>/<name>.txt`,
  owned by the `examples` agent (#312), shipped in the release zip via
  `INCLUDES`, resolved at runtime relative to the install root.

## Implementation Steps

### Step 1 — Document the examples folder

- `docs/agents/folder-structure.md`: add an `examples/` row — shipped,
  terminal-printed walkthroughs, one subfolder per command; owned by the
  `examples` agent. (If #312 already added the row, just refine it with the
  first file, `examples/kube/end_to_end.txt`.)
- `docs/agents/tingle-release-zip.md`: add `examples` to the documented
  `INCLUDES` allowlist.
- `docs/agents/architecture.md`: in the kube section, note the `example`
  subcommand, that it is dispatched before `KubeConfig()` is loaded (no
  config, AWS or cluster access, also in completion), and that it prints
  `examples/kube/end_to_end.txt` resolved from the install root.

## Files to Change

- `docs/agents/folder-structure.md` — `examples/` row.
- `docs/agents/tingle-release-zip.md` — `INCLUDES` list.
- `docs/agents/architecture.md` — kube `example` subcommand.
