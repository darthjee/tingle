# Plan: Codacy: Absolute rule without escape hatch (AGENTS.md:30)

Issue: [195-codacy-absolute-rule-without-escape-hatch-agents-md-30.md](../../issues/195-codacy-absolute-rule-without-escape-hatch-agents-md-30.md)

## Overview
Add a narrow, concrete exception to each of the six absolute rules in the
**Boundaries** section of `AGENTS.md` that Codacy's Agentlinter flags with
`Agentlinter_clarity_escape-hatch-missing` (lines 30, 32, 33, 35, 37, 39 —
issues #195–#200). This fix resolves all six findings in a single change.

## Context
Each flagged rule is an absolute `**Must**` / `**Never**` with no guidance
for legitimate exceptions. Line 29 (`**Never**: introduce cross-script
dependencies unless truly shared.`) is not flagged because it already has an
inline exception, and it is the style to follow. Some rules are also stricter
than the repo's reality. For example, line 35 forbids root-level docs that
exist today (`README.md`, `AGENTS.md`, `CLAUDE.md`, `DOCKERHUB_DESCRIPTION.md`,
`.github/` templates), and line 33 forbids tooling that lives outside the
language folders (`Makefile`, `scripts/`, `install/`, `completions/`,
`commands/`, `docker-compose.yml`, `.circleci/`, `.github/`).

`AGENTS.md` is a root-level file, so the `architect` owns this change. No
specialist agent has work.

## Implementation Steps

### Step 1 — Add escape hatches to the Boundaries rules
In `AGENTS.md`, change each flagged Boundaries entry as follows. Keep the
`**Must**` / `**Never**` prefix and the existing wrapping style (continuation
lines indented by two spaces, lines of about 76 characters or fewer):

- **Must**: document a script's usage and dependencies in a header comment
  whenever it is added or modified, unless the change does not affect its
  usage or dependencies (e.g. typo fixes, formatting, internal refactors).
- **Must**: add a new script to the table in `README.md`, unless it is an
  internal helper not meant to be invoked directly.
- **Never**: place implementation code outside `shell/`, `python/`,
  `node/`, or `bin/`, except for build, release, install and CI tooling and
  config (e.g. `Makefile`, `scripts/`, `install/`, `completions/`,
  `commands/`, `docker-compose.yml`, `.circleci/`, `.github/`).
- **Never**: place documentation anywhere other than `docs/guides/`
  (user-facing guides) or `docs/agents/` (agent-facing docs), except for
  root-level files required by tooling or convention (`README.md`,
  `AGENTS.md`, `CLAUDE.md`, `DOCKERHUB_DESCRIPTION.md`, and
  templates/instructions under `.github/`).
- **Must**: update the relevant file(s) under `docs/agents/` whenever an
  architectural change is made; if no existing file covers the area, add
  one and list it in the Documentation table.
- **Must**: update the matching guide in `docs/guides/` whenever a
  command's user-visible behaviour changes; if the command has no guide
  yet, note that in the PR description.

Leave line 29 (`**Never**: introduce cross-script dependencies…`) as it is.

### Step 2 — Bump the update date
Set `Last updated:` near the top of `AGENTS.md` to the implementation date.
`CLAUDE.md` does not summarise the Boundaries rules, so it needs no change
beyond keeping its own `Last updated:` line consistent, if the repo convention
requires both to match.

## Files to Change
- `AGENTS.md` — add an escape hatch to six Boundaries rules and bump
  `Last updated:`.

## Notes
- The fix is purely wording. There is no code change and no CI job lints
  Markdown locally, so verification is the Codacy re-analysis on the PR.
- The PR description should reference #196–#200 (e.g. `Closes #196`, …)
  so those sibling issues close together with #195.
- Line numbers shift once the entries grow. Codacy tracks findings by
  content, so the old findings should disappear, not move.
