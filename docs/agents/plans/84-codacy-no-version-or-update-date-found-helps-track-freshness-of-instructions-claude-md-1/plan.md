# Plan: Codacy: no version or update date found in CLAUDE.md

Issue: [84-codacy-no-version-or-update-date-found-helps-track-freshness-of-instructions-claude-md-1.md](../../issues/84-codacy-no-version-or-update-date-found-helps-track-freshness-of-instructions-claude-md-1.md)

## Overview
Codacy's documentation linter flagged `CLAUDE.md:1` for missing a version or update date. Add a manually-maintained `Last updated: YYYY-MM-DD` line near the top of both `CLAUDE.md` and `AGENTS.md`, so the finding is resolved and both files carry a low-ceremony freshness signal.

## Context
`CLAUDE.md` is a one-line pointer to `AGENTS.md`, which holds the actual project conventions. Neither file currently indicates when it was last updated. The fix is a manual date marker (no semantic versioning, no automated bump) added to both files, updated by hand whenever the corresponding file's content meaningfully changes.

## Implementation Steps

### Step 1 — Add freshness marker to AGENTS.md
Insert a `_Last updated: YYYY-MM-DD_` line directly below the `# Project Instructions` title (using today's date at the time this step is implemented), before the existing description paragraph.

### Step 2 — Add freshness marker to CLAUDE.md
Insert the same `_Last updated: YYYY-MM-DD_` line into `CLAUDE.md`, alongside its existing pointer line to `AGENTS.md`, keeping the file readable as a short pointer (e.g. the pointer sentence followed by the marker line).

## Files to Change
- `AGENTS.md` — add a `Last updated: YYYY-MM-DD` line below the title.
- `CLAUDE.md` — add a `Last updated: YYYY-MM-DD` line alongside the pointer to `AGENTS.md`.

## Notes
- No automated tooling enforces or bumps this date — it's a manual convention. Future edits to either file should update its own marker.
- This issue and plan only touch root-level files (`CLAUDE.md`, `AGENTS.md`); none of the repo's language specialists (`cli`, `node`, `python`, `shell`) or `product-owner` (scoped to `docs/agents/` content) own these files, so the architect implements this directly per its own "root-level files" scope.
