# Issue: Codacy: 17 instruction items with no priority signals. The agent can't distinguish critical from optional. (AGENTS.md:1)

## Description
Codacy's Agentlinter flagged `AGENTS.md:1` (pattern `Agentlinter_clarity_priority-signal-missing`, category Documentation): "17 instruction items with no priority signals. The agent can't distinguish critical from optional."

## Problem
`AGENTS.md` lists its Conventions and Boundaries items as flat bullet lists with no explicit priority markers (e.g. `MUST`, `SHOULD`, `NEVER`). An agent reading the file can't tell at a glance which of the 17 instruction items are hard constraints versus soft preferences, even though `Boundaries` is implicitly the hard-constraint section and `Conventions` the softer one.

## Expected Behavior
Instruction items in `AGENTS.md` carry an explicit priority signal so an agent (or a human skimming the file) can distinguish critical rules from optional guidance at a glance.

## Solution
Review the bullet lists under `## Conventions` and `## Boundaries` in `AGENTS.md`, and prefix each item with an explicit priority marker consistent with its section's intent — e.g. `**Must**:` / `**Never**:` for items under `Boundaries`, and `**Should**:` for items under `Conventions`. Keep the change minimal and consistent with the file's existing tone; do not restructure the sections themselves.

## Benefits
Resolves the Codacy finding and gives both human contributors and AI agents a clearer signal of which instructions are non-negotiable.
