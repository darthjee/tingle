# Issue: Codacy: no version or update date found in CLAUDE.md

## Description
Codacy's documentation linter flagged `CLAUDE.md:1` for missing a version or update date at the top of the file. This marker helps readers (human or agent) judge how current the agent instructions are.

## Problem
`CLAUDE.md` is a one-line pointer to `AGENTS.md`, which holds the actual project conventions. Neither file currently carries any freshness indicator (version number or last-updated date), so there's no quick way to tell whether the instructions reflect the current state of the repo.

## Expected Behavior
Both `CLAUDE.md` and `AGENTS.md` carry a clear, low-maintenance freshness marker near the top, satisfying the Codacy pattern `Agentlinter_structure_has-version-or-update-date`.

## Solution
Add a `Last updated: YYYY-MM-DD` line to the top of both files:
- In `AGENTS.md`, right below the `# Project Instructions` title.
- In `CLAUDE.md`, right below (or alongside) its pointer line to `AGENTS.md`.

Both lines are updated by hand whenever the corresponding file's content meaningfully changes; no automated bump or semantic-versioning scheme is introduced.

## Benefits
- Resolves the Codacy finding.
- Gives contributors and agents a quick, low-ceremony signal of how current the instructions are, without requiring a version-numbering convention.
