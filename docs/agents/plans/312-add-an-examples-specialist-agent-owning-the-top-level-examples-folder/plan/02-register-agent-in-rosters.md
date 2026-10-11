# Register the agent in the root-level rosters

Add `examples` wherever the agent roster is listed, keeping the wording
parallel to the existing `guide` entries:

- `AGENTS.md`, `## Tools` list — add after `guide`:
  "`examples` — content under `examples/` (shipped, terminal-printed
  walkthroughs, one folder per `tingle` command)."
- `CLAUDE.md`, `## Tools` — add `examples` to the agent name list
  (`architect`, `cli`, `node`, `python`, `shell`, `product-owner`, `guide`,
  `examples`) and bump the `Last updated` date.
- `.claude/agents/architect.md`:
  - in `## Your scope`, after the `guide` delegation sentence, add
    "Shipped examples (`examples/`) belong to `examples` — delegate to it
    likewise.";
  - in the `## Specialist agents` table, add the row
    `| `examples` | `examples/` — shipped, terminal-printed walkthroughs, one folder per `tingle` command |`.

## Files to Change
- `AGENTS.md` — add `examples` to the Tools list.
- `CLAUDE.md` — add `examples` to the agent list; bump `Last updated`.
- `.claude/agents/architect.md` — delegation sentence and roster table row.
