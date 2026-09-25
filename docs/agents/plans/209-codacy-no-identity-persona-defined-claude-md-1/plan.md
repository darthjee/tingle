# Plan: Codacy: No identity/persona defined (CLAUDE.md:1)

Issue: [209-codacy-no-identity-persona-defined-claude-md-1.md](../../issues/209-codacy-no-identity-persona-defined-claude-md-1.md)

## Overview
Add the persona sentence from `AGENTS.md`, word for word, to `CLAUDE.md` so
Codacy's Agentlinter (`Agentlinter_completeness_has-identity`) stops flagging
`CLAUDE.md:1`. `CLAUDE.md` is a root-level file, so the architect owns this
change; no specialist agent is involved.

## Context
#89 added the persona to `AGENTS.md` only and kept `CLAUDE.md` as a thin
pointer, accepting the Codacy finding. Later fixes (#69, #88, #113, #174) added
Stack and Documentation summary sections to `CLAUDE.md`, so it no longer is a
thin pointer. This issue reverses #89's choice for `CLAUDE.md` only.
`AGENTS.md` and `.github/copilot-instructions.md` stay unchanged.

## Implementation Steps

### Step 1 — Add the persona to `CLAUDE.md`
Insert this paragraph right after the `## Project Instructions` heading, before
the existing "See [AGENTS.md](AGENTS.md)…" paragraph, with a blank line on each
side:

```markdown
You are an assistant helping maintain Tingle, a personal collection of small,
independent utility scripts.
```

The wording and line wrap must match `AGENTS.md` exactly. Do not add a new
heading. Bump the `Last updated:` line at the bottom of `CLAUDE.md` to the
implementation date.

## Files to Change
- `CLAUDE.md` — add the persona paragraph under `## Project Instructions`, bump
  `Last updated:`.

## Notes
- No CI job covers `CLAUDE.md` (CircleCI only runs `ruff` and the Python
  tests), so the only check is the Codacy Agentlinter result on the PR.
- If the persona in `AGENTS.md` changes later, update `CLAUDE.md` in the same
  change to keep them in sync.
