# Plan: Codacy: Emphasis used instead of a heading (CLAUDE.md:17)

Issue: [113-codacy-emphasis-used-instead-of-a-heading-claude-md-17.md](../issues/113-codacy-emphasis-used-instead-of-a-heading-claude-md-17.md)

## Overview
Codacy's markdownlint (MD036) flags the `_Last updated: YYYY-MM-DD_` line in `CLAUDE.md` for using emphasis where plain text/heading would be more appropriate. `AGENTS.md` has the identical pattern and would trip the same rule, so both files are fixed together.

## Context
Both `CLAUDE.md:17` and `AGENTS.md:3` currently render the freshness marker as italic emphasis (`_Last updated: 2026-09-20_`). The fix is purely textual — drop the surrounding underscores, keeping the line's position and content otherwise unchanged.

## Implementation Steps

### Step 1 — Drop emphasis from the "Last updated" line in both files
In `CLAUDE.md` and `AGENTS.md`, replace `_Last updated: YYYY-MM-DD_` with plain text `Last updated: YYYY-MM-DD` (no surrounding underscores). No other content on the line changes.

## Files to Change
- `CLAUDE.md` — drop underscores from the `_Last updated: 2026-09-20_` line (line 17).
- `AGENTS.md` — drop underscores from the `_Last updated: 2026-09-20_` line (line 3).

## Notes
- Root-level files with no single specialist agent owner (per `.claude/agents/` descriptions), so this plan stays a single `plan.md` handled directly by the architect rather than split across agents.
