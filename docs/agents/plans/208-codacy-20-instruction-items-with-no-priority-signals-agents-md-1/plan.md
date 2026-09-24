# Plan: Codacy: 20 instruction items with no priority signals (AGENTS.md:1)

Issue: [208-codacy-20-instruction-items-with-no-priority-signals-agents-md-1.md](../../issues/208-codacy-20-instruction-items-with-no-priority-signals-agents-md-1.md)

## Overview

Make `AGENTS.md` satisfy Agentlinter's `clarity/priority-signal-missing`
rule by switching the mixed-case priority markers to the uppercase RFC 2119
keywords the rule recognises, and document that convention in one line so
it is not reverted. This is a root-level, cross-cutting file, so the
`architect` owns the change.

## Context

The rule (`src/engine/rules/clarity.ts` in seojoonkim/agentlinter) checks the
file as a whole. When a file has at least 10 bullet lines, the file passes if
any single line matches the case-sensitive regex
`\b(critical|important|must|required|optional|nice.?to.?have|priority|P[0-3]|⚠️|🔴|MUST|SHOULD|MAY)\b`.
The `**Must**` / `**Should**` / `**Never**` markers added in #112 match none
of these alternatives, so the rule counts every bullet in the file
(3 Stack + 3 Conventions + 7 Boundaries + 7 Tools = 20).
`clarity/escape-hatch-missing` is case-insensitive, so changing the case
does not affect it.

## Implementation Steps

### Step 1 — Uppercase the priority markers

In `AGENTS.md`, replace every `**Should**` with `**SHOULD**` (Conventions,
3 items), every `**Must**` with `**MUST**`, and every `**Never**` with
`**NEVER**` (Boundaries, 7 items). Do not change any other wording. Do not add
markers to the Stack or Tools bullets, because they are informational and the
rule only needs one matching line.

### Step 2 — Document the convention and bump the date

Add a one-line note directly under `## Conventions`, before the bullet list.
The note says the priority keywords (**MUST**, **SHOULD**, **NEVER**) follow
RFC 2119 and are uppercase on purpose. Example:

```markdown
Priority keywords (**MUST**, **SHOULD**, **NEVER**) follow RFC 2119 and are
written in uppercase on purpose.
```

Set `Last updated:` in `AGENTS.md` to the implementation date. `CLAUDE.md`
only summarises `AGENTS.md` and does not repeat the markers, so it needs no
change beyond its own `Last updated:` if the repo convention requires it.

## Files to Change

- `AGENTS.md` — uppercase the priority markers, add the RFC 2119 note, and
  bump `Last updated:`.

## Notes

- Verification: `grep -nE '\b(MUST|SHOULD)\b' AGENTS.md` should return
  matches, and `grep -nE '\*\*(Must|Should|Never)\*\*' AGENTS.md` should
  return nothing.
- The Codacy MCP server was unavailable during refinement. The analysis is
  based on agentlinter's open-source code, which may differ slightly from the
  version Codacy runs.
- CI (`.circleci/config.yml`) only lints and tests `python/`. No CI job
  covers this Markdown change.
