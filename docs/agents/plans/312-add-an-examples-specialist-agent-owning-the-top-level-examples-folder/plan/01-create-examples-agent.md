# Create the examples agent file

Create `.claude/agents/examples.md`, mirroring the shape of
`.claude/agents/guide.md`:

- Frontmatter: `name: examples`; `description: Tingle examples owner. Use for
  any task involving examples/ content — shipped, terminal-printed
  walkthroughs, one folder per tingle command.`; `tools: Read, Edit, Write, Bash`.
- Intro line: "You are the examples agent for the Tingle project — a personal
  repository of everyday utility scripts."
- `## Your scope`: owns `examples/`, organised as
  `examples/<command>/<name>.txt` (e.g. `examples/kube/end_to_end.txt`,
  printed by `tingle kube example`). Does NOT touch `python/`, `shell/`,
  `node/`, `bin/` or `commands/` implementation (including the code that
  reads/prints these files), `docs/guides/` (`guide`), `docs/agents/`
  (`product-owner`), or root-level files (`architect`).
- `## Conventions`:
  - plain ASCII, lines within ~80 columns;
  - one linear, step-by-step walkthrough per file;
  - clearly fictional identifiers only (e.g. AWS account `123456789012`),
    never values from a real environment and never secrets;
  - keep each example in sync with the command's real behaviour — its
    `long_help` in `commands/*.json` and `docs/guides/<command>.md`;
  - files under `examples/` ship in the release, so they must stay free of
    anything that should not be distributed.

## Files to Change
- `.claude/agents/examples.md` — new agent definition.
