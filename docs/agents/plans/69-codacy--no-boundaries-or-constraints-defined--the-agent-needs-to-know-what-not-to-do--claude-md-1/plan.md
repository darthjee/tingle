# Plan: Codacy: No boundaries or constraints defined. The agent needs to know what NOT to do (CLAUDE.md:1)

Issue: [69-codacy--no-boundaries-or-constraints-defined--the-agent-needs-to-know-what-not-to-do--claude-md-1.md](../issues/69-codacy--no-boundaries-or-constraints-defined--the-agent-needs-to-know-what-not-to-do--claude-md-1.md)

## Overview

Add an explicit "Boundaries" section to `AGENTS.md` (the file `CLAUDE.md` points to) listing
things an agent must NOT do in this repo, derived from conventions already documented elsewhere
in `AGENTS.md`. This satisfies Codacy's `Agentlinter_completeness_has-boundaries` check on
`CLAUDE.md:1`, which currently has no content of its own beyond the redirect.

## Context

`CLAUDE.md` is a one-line pointer to `AGENTS.md` plus a `_Last updated:` date. `AGENTS.md`
documents the stack and a `## Conventions` section (positive practices: keep scripts
independent, document usage, add new scripts to the `README.md` table) but never states what an
agent should avoid doing. Codacy's agent linter flags this absence as a BestPractice warning
because an agent reading only `CLAUDE.md`/`AGENTS.md` has no stated constraints.

## Implementation Steps

### Step 1 — Add a "Boundaries" section to AGENTS.md

Add a `## Boundaries` section to `AGENTS.md`, placed after `## Conventions` and before
`## Documentation`, listing explicit "do not" rules consistent with the repo's existing norms:

- Do not introduce cross-script dependencies unless truly shared.
- Do not add or modify a script without documenting its usage/dependencies in a header comment.
- Do not add a new script without also adding it to the `README.md` table.
- Do not place implementation code outside `shell/`, `python/`, `node/`, or `bin/`, or
  documentation outside `docs/agents/`.
- Do not make an architectural change without updating the relevant file(s) under
  `docs/agents/`.

Bump `AGENTS.md`'s `_Last updated:` date to the date this change is committed.

### Step 2 — Bump CLAUDE.md's last-updated date

`CLAUDE.md` itself is unchanged in substance (it stays a pointer to `AGENTS.md`), but bump its
`_Last updated:` date to match, since the content it points to changed.

## Files to Change

- `AGENTS.md` — add the new `## Boundaries` section; bump `_Last updated:`.
- `CLAUDE.md` — bump `_Last updated:` to match.

## Notes

- No code/script changes are needed — this is a documentation-only fix targeting the root-level
  project instructions, squarely within the architect's own scope (no specialist agent has work
  here).
- Re-running Codacy's agent linter after this change should clear the
  `Agentlinter_completeness_has-boundaries` finding on `CLAUDE.md:1`.
