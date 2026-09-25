# Plan: Codacy: No tool documentation found (CLAUDE.md:1)

Issue: [210-codacy-no-tool-documentation-found-claude-md-1.md](../../issues/210-codacy-no-tool-documentation-found-claude-md-1.md)

## Overview

Add a short `## Tools` section to `CLAUDE.md` that names the specialist agents
and links to `AGENTS.md#tools`, so Codacy's Agentlinter
(`Agentlinter_completeness_has-tools`) no longer flags `CLAUDE.md:1`.

## Context

`CLAUDE.md` currently has `## Project Instructions`, `## Stack` and
`## Documentation` sections, each a short summary plus a link into
`AGENTS.md`. `AGENTS.md` already has a `## Tools` section listing the agents
defined under `.claude/agents/` (`architect`, `cli`, `node`, `python`,
`shell`, `product-owner`, `guide`) and what each owns. `AGENTS.md` is the
single source of truth, so `CLAUDE.md` must summarise, not copy, the
per-agent scope list.

## Implementation Steps

### Step 1 — Add `## Tools` section to `CLAUDE.md`

Insert a new `## Tools` section between `## Stack` and `## Documentation`,
matching the style of those sections (short prose wrapped at ~78 columns,
ending with a link). Suggested content:

```markdown
## Tools

Specialist agents are defined under `.claude/agents/` (`architect`, `cli`,
`node`, `python`, `shell`, `product-owner`, `guide`); delegate work to the
agent that owns the area. See [AGENTS.md](AGENTS.md#tools) for each agent's
scope.
```

Update the trailing `Last updated:` line to the date of the change. Do not
touch `AGENTS.md` or `.claude/agents/`.

## Files to Change

- `CLAUDE.md` — add the `## Tools` section and bump `Last updated:`.

## Notes

- CI (`.circleci/config.yml`) only runs `ruff`/tests under `python/`, so no
  CI job covers this change; verification is Codacy's Agentlinter on the PR.
- Keep the agent list in sync with `AGENTS.md#tools`; if an agent is added
  or removed later, both files need updating.
