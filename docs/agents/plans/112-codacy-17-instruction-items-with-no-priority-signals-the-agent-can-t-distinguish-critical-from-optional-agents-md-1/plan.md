# Plan: Codacy: 17 instruction items with no priority signals. The agent can't distinguish critical from optional. (AGENTS.md:1)

Issue: [112-codacy-17-instruction-items-with-no-priority-signals-the-agent-can-t-distinguish-critical-from-optional-agents-md-1.md](../../issues/112-codacy-17-instruction-items-with-no-priority-signals-the-agent-can-t-distinguish-critical-from-optional-agents-md-1.md)

## Overview
`AGENTS.md`'s `## Conventions` and `## Boundaries` bullet lists have no explicit priority markers, so an agent can't tell at a glance which items are hard constraints versus soft preferences. Prefix each bullet in both sections with a bold marker matching its section's intent.

## Context
- `## Conventions` (3 bullets) holds softer guidance — prefix each with `**Should**:`.
- `## Boundaries` (5 bullets) holds hard constraints, phrased as "Do not ..." — prefix each with `**Never**:` (rephrasing the leading "Do not" away since the marker now carries that meaning), except any bullet that is more naturally a positive requirement, which should use `**Must**:` instead.
- Keep wording changes minimal — only add the marker and adjust the sentence to read naturally with it; do not restructure the sections or reorder items.
- This is a root-level file (`AGENTS.md`), owned by `architect` per `AGENTS.md`'s own Tools table — no specialist agent's scope covers it.

## Implementation Steps

### Step 1 — Add priority markers to Conventions and Boundaries
Edit `AGENTS.md`:
- Under `## Conventions`, prefix each of the 3 bullets with `**Should**:`.
- Under `## Boundaries`, prefix each of the 5 bullets with `**Never**:` (rewording "Do not X" to "X" after the marker, e.g. `**Never**: introduce cross-script dependencies unless truly shared.`).
- Re-read both sections afterward to confirm the result still reads naturally and no bullet's meaning changed.

## Files to Change
- `AGENTS.md` — add `**Should**:` / `**Never**:` priority prefixes to the `## Conventions` and `## Boundaries` bullets.

## Notes
- No CI job in `.circleci/config.yml` covers markdown/docs files, so no `## CI Checks` section applies.
- `CLAUDE.md` only summarizes `AGENTS.md` and does not duplicate these bullet lists, so it needs no change.
