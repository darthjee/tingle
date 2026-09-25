# Issue: Codacy: No tool documentation found (CLAUDE.md:1)

## Description
Codacy's Agentlinter flagged `CLAUDE.md:1` (pattern `Agentlinter_completeness_has-tools`, category Documentation, severity Info): "No tool documentation found. The agent doesn't know what tools are available or how to use them."

## Problem
`CLAUDE.md` has Project Instructions, Stack and Documentation sections, but nothing about the specialist agents available. `AGENTS.md` already has a `## Tools` section listing the agents under `.claude/agents/` (`architect`, `cli`, `node`, `python`, `shell`, `product-owner`, `guide`) and what each owns, but `CLAUDE.md` neither summarises nor links it.

## Expected Behavior
- `CLAUDE.md` has a short `## Tools` section that names the specialist agents and links to [`AGENTS.md#tools`](AGENTS.md#tools) for their scopes.
- Agentlinter no longer reports `Agentlinter_completeness_has-tools` on `CLAUDE.md`.
- `AGENTS.md` stays the single source of truth: the `CLAUDE.md` section is a summary, not a copy of the per-agent scope list.

## Solution
- Add a `## Tools` section to `CLAUDE.md` between `## Stack` and `## Documentation`, in the same style as those sections: one or two sentences saying that specialist agents are defined under `.claude/agents/`, naming them (`architect`, `cli`, `node`, `python`, `shell`, `product-owner`, `guide`), telling the agent to delegate to the one that owns the area, and linking to `AGENTS.md#tools`.
- Update the `Last updated:` line in `CLAUDE.md` to the date of the change.
- Only `CLAUDE.md` changes; no changes to `AGENTS.md` or `.claude/agents/`.

## Benefits
Agents that only load `CLAUDE.md` learn which specialist agents exist and where to find their scopes, and the Codacy finding is resolved.
