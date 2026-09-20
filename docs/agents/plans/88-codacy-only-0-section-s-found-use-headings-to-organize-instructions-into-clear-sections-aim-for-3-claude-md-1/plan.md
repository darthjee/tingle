# Plan: Codacy: Only 0 section(s) found. Use ## headings to organize instructions into clear sections (aim for 3+). (CLAUDE.md:1)

Issue: [88-codacy-only-0-section-s-found-use-headings-to-organize-instructions-into-clear-sections-aim-for-3-claude-md-1.md](../../issues/88-codacy-only-0-section-s-found-use-headings-to-organize-instructions-into-clear-sections-aim-for-3-claude-md-1.md)

## Overview
`CLAUDE.md` is a one-line pointer to `AGENTS.md` and has no `##` headings, so Codacy's `Agentlinter_structure_has-sections` pattern reports 0 sections. Keep `AGENTS.md` as the source of truth and give `CLAUDE.md` a short structured summary with at least 3 `##` sections, each summarizing or linking to the matching `AGENTS.md` content.

## Context
- `CLAUDE.md` currently holds a single sentence (`See [AGENTS.md](AGENTS.md) for project instructions.`) and a `_Last updated_` line.
- `AGENTS.md` already has `## Stack`, `## Conventions`, `## Boundaries` and `## Documentation`.
- The issue confirms "Project Instructions" as one section; the others were left open, with Stack, Boundaries and Documentation as candidates.
- `CLAUDE.md` is a root-level file. No specialist agent owns it, so this is cross-cutting work for the architect.

## Implementation Steps

### Step 1 — Restructure `CLAUDE.md`
Rewrite `CLAUDE.md` with at least 3 `##` sections:
- `## Project Instructions` — states that `AGENTS.md` is the source of truth and links to it.
- `## Stack` — one-line summary of the three stacks (`shell/`, `python/`, `node/`), pointing to `AGENTS.md#stack`.
- `## Documentation` — pointer to `docs/agents/` and `AGENTS.md#documentation`.

Keep each section to a line or two of summary or link, with no full duplication of `AGENTS.md`. Update the `_Last updated_` line to the date of the change.

### Step 2 — Verify
- Confirm `grep -c '^## ' CLAUDE.md` is at least 3.
- Confirm `AGENTS.md` is untouched and all links in `CLAUDE.md` resolve.
- If the Codacy CLI is available, run it on `CLAUDE.md` and check that `Agentlinter_structure_has-sections` no longer fires.

## Files to Change
- `CLAUDE.md` — add 3+ `##` sections, each a short summary or link to `AGENTS.md`, and update the last-updated date.

## Notes
- The sections beyond "Project Instructions" were not fixed in the issue discussion. Stack and Documentation are the proposed picks, and Boundaries could replace or supplement either.
- `.github/copilot-instructions.md` is not in scope for this issue.
