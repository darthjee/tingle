# Issue: Codacy: Only 0 section(s) found. Use ## headings to organize instructions into clear sections (aim for 3+). (CLAUDE.md:1)

## Description
Codacy flagged `CLAUDE.md:1` with the `Agentlinter_structure_has-sections` pattern (category: Documentation, severity: Info). Codacy issue ID: `711b6236e95bff092e09f4e85fc915e9`.

Message: _Only 0 section(s) found. Use ## headings to organize instructions into clear sections (aim for 3+)._

## Problem
`CLAUDE.md` is currently a one-line pointer to `AGENTS.md` (plus a last-updated date) and contains no `##` headings, so the linter counts 0 sections. The real project instructions, which already have several `##` sections, live in `AGENTS.md`; the linter only sees `CLAUDE.md`.

## Expected Behavior
`CLAUDE.md` contains at least 3 `##` headings that organize its instructions, and Codacy no longer reports `Agentlinter_structure_has-sections` for it.

## Solution
Keep `AGENTS.md` as the single source of truth and keep `CLAUDE.md` a pointer, but give `CLAUDE.md` a short, structured summary with at least 3 `##` sections. Each section is a brief summary of, or a link back to, the matching `AGENTS.md` content, so nothing is duplicated in full.

- **Project Instructions** — confirmed. It holds the title/pointer to `AGENTS.md`.
- The remaining sections (to reach 3+) are still to be chosen. Candidates are Stack, Boundaries and Documentation.

Update the `_Last updated_` date in `CLAUDE.md` when it is edited.

## Benefits
- Clears the Codacy `Agentlinter_structure_has-sections` finding.
- Preserves the `init-claude` convention (`AGENTS.md` as source of truth) and avoids drift between two full copies.
