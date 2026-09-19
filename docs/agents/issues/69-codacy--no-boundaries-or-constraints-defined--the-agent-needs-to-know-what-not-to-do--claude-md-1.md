# Codacy: No boundaries or constraints defined. The agent needs to know what NOT to do (CLAUDE.md:1)

## Context

Codacy's agent-linter flagged `CLAUDE.md:1` with the `Agentlinter_completeness_has-boundaries`
pattern (category: BestPractice, severity: Warning) — Codacy issue ID
`2a3c3cbcb2cf9220ac632fc38f9d0088`. `CLAUDE.md` currently only points to `AGENTS.md` for
instructions and carries no content of its own that defines boundaries or constraints for an
AI agent working in this repository. `AGENTS.md`, which `CLAUDE.md` delegates to, likewise
documents stack, conventions, and documentation layout, but never states what an agent should
avoid doing.

## What needs to be done

Add an explicit "boundaries" or "constraints" section to the project instructions so an agent
reading `CLAUDE.md`/`AGENTS.md` knows what NOT to do, alongside the existing conventions. Since
`CLAUDE.md` is a thin pointer to `AGENTS.md`, the new content should live in `AGENTS.md` (root
scope), keeping `CLAUDE.md` as the redirect. Constraints should reflect this repo's existing
norms, e.g.:

- Do not introduce cross-script dependencies unless truly shared (already implied, make explicit
  as a "don't").
- Do not add a new script without documenting usage/dependencies in a header comment and without
  adding it to the `README.md` table.
- Do not place implementation code outside the established `shell/`, `python/`, `node/`, `bin/`
  folders, or documentation outside `docs/agents/`.
- Do not skip updating `docs/agents/` when an architectural change is made.

## Acceptance criteria

- [ ] `AGENTS.md` (or `CLAUDE.md`, if more appropriate) contains an explicit section listing
      boundaries/constraints — things an agent must NOT do — consistent with the existing
      conventions already documented in the repo.
- [ ] `CLAUDE.md`'s `_Last updated:` date (and `AGENTS.md`'s, if changed) is bumped to reflect
      the edit.
- [ ] The Codacy finding for `CLAUDE.md:1` (`Agentlinter_completeness_has-boundaries`) no longer
      applies after the change.
