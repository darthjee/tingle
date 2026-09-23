# Create the guide agent

Add a new specialist agent, `guide`, that owns `docs/guides/`. Copy the
structure of `.claude/agents/product-owner.md`: the frontmatter (`name`,
`description`, `tools: Read, Edit, Write, Bash`), then "Your scope" and
"Conventions" sections.

- **Scope:** `docs/guides/README.md` (the guides index) and one guide per
  `tingle` command at `docs/guides/<command>.md`.
- **Must not touch:** `shell/`, `python/`, `node/`, `bin/`, `commands/`,
  `docs/agents/` (owned by `product-owner`), or root files (owned by
  `architect`).
- **Conventions:**
  - Write for end users, not agents.
  - Keep each guide in sync with the command's real behaviour: its
    `long_help` in `commands/*.json` and the script's header.
  - Add or refresh the command's entry in `docs/guides/README.md` whenever a
    guide is added.

Also add `guide` to the specialist table in `.claude/agents/architect.md`,
and note that `docs/guides/` belongs to `guide`, next to the existing
"`docs/agents/` belongs to `product-owner`" line. Tighten the
`product-owner` row description to "`docs/agents/` — agent-facing
documentation" so the two scopes don't overlap.

## Files to Change
- `.claude/agents/guide.md` — new agent definition.
- `.claude/agents/architect.md` — add `guide` to the specialist table and
  delegation note; clarify the `product-owner` row.
