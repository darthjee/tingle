# Plan: Codacy: No tool documentation found. The agent doesn't know what tools are available or how to use them. (CLAUDE.md:1)

Issue: [86-codacy-no-tool-documentation-found-the-agent-doesn-t-know-what-tools-are-available-or-how-to-use-them-claude-md-1.md](../../issues/86-codacy-no-tool-documentation-found-the-agent-doesn-t-know-what-tools-are-available-or-how-to-use-them-claude-md-1.md)

## Overview
Add a short `## Tools` section to `AGENTS.md` listing the specialist agents defined under `.claude/agents/` and what each one is for. This satisfies the Codacy Agentlinter `has-tools` completeness check and gives an agent an explicit list of who to delegate to. `CLAUDE.md` and `.github/copilot-instructions.md` stay untouched, following the approach used for #89.

## Context
`AGENTS.md` is the single source of truth for project instructions; `CLAUDE.md` is a thin pointer to it. Neither file mentions the six specialist agents in `.claude/agents/` (`architect`, `cli`, `node`, `product-owner`, `python`, `shell`). Test/lint commands, the `bin/tingle` CLI and the release scripts are explicitly out of scope for this issue. `AGENTS.md` lives at the repo root, which no specialist owns, so the architect makes this change directly.

## Implementation Steps

### Step 1 — Add the `## Tools` section to `AGENTS.md`
Insert a `## Tools` section in `AGENTS.md`, placed after `## Boundaries` and before `## Documentation` so that it sits with the other agent-behaviour sections and ahead of the documentation index. Content: a one-sentence intro saying the specialist agents live in `.claude/agents/` (which holds their full descriptions and is the source of truth, so nothing is duplicated), then one bullet per agent:

- `architect` — cross-cutting tasks, multi-agent coordination, root-level files.
- `cli` — entry points under `bin/` (arg parsing, `--help`, exit codes, dispatch).
- `node` — Node.js scripts under `node/`.
- `python` — Python scripts under `python/`.
- `shell` — Bash/Shell scripts under `shell/`.
- `product-owner` — content under `docs/agents/` (architecture, flow, folder structure, contributing, issues, plans).

Keep the wording consistent with each agent's `description:` front-matter in `.claude/agents/*.md`.

### Step 2 — Refresh the "Last updated" date
`AGENTS.md` carries a `_Last updated: <date>_` line under its title (added for #84). Update it to the date of the change so the file stays consistent. Leave `CLAUDE.md`'s own date line alone, since that file is not modified.

## Files to Change
- `AGENTS.md` — add the `## Tools` section and update the `_Last updated_` line.

## Notes
- Do not modify `CLAUDE.md` or `.github/copilot-instructions.md`. Codacy may keep flagging `CLAUDE.md:1` on its own, an accepted tradeoff of the redirect convention (same as #89).
- No CI job applies: `.circleci/config.yml` only lints and tests `python/`, and this change touches only a Markdown file.
- If an agent is later added to or removed from `.claude/agents/`, the `## Tools` list in `AGENTS.md` has to be updated by hand; it is not generated.
