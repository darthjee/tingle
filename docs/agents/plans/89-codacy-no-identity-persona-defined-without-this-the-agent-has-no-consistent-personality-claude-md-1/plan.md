# Plan: Codacy: No identity/persona defined. Without this, the agent has no consistent personality. (CLAUDE.md:1)

Issue: [89-codacy-no-identity-persona-defined-without-this-the-agent-has-no-consistent-personality-claude-md-1.md](../../issues/89-codacy-no-identity-persona-defined-without-this-the-agent-has-no-consistent-personality-claude-md-1.md)

## Overview

Codacy's Agentlinter flagged `CLAUDE.md:1` for missing an identity/persona statement. `CLAUDE.md` and `.github/copilot-instructions.md` are deliberately thin pointers to `AGENTS.md` and stay that way; the actual fix is a short, generic persona paragraph added to the top of `AGENTS.md`, ahead of the existing "Project Instructions" content.

## Context

`AGENTS.md` currently opens directly with `# Project Instructions` and a description of the Tingle repo, without ever stating who the assistant is or what role it plays. This is a docs-only, root-level file, with no code-affecting change.

## Implementation Steps

### Step 1 — Add a persona paragraph to AGENTS.md

Add a short, neutral identity/persona statement immediately below the `# Project Instructions` heading (and above the `_Last updated:_` line, updating that date to the day this change lands), e.g.:

> You are an assistant helping maintain Tingle, a personal collection of small, independent utility scripts.

Keep it consistent in tone with the repo's existing self-description ("a personal repository of everyday utility scripts") already present a few lines below. Do not touch `CLAUDE.md` or `.github/copilot-instructions.md` — they remain unchanged, thin pointers to `AGENTS.md`.

## Files to Change

- `AGENTS.md` — add a one- or two-sentence persona/identity statement near the top, and bump the `_Last updated:_` date.

## Notes

- `CLAUDE.md:1` may keep being flagged by Codacy on its own, since it stays a one-line redirect by design (the `init-claude` convention) — accepted tradeoff per issue discussion.
- No CI job in `.circleci/config.yml` covers root-level Markdown files (`lint`/`tests` only run against `python/`), so no `## CI Checks` section applies.
