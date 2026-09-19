# Issue: Codacy: No identity/persona defined. Without this, the agent has no consistent personality. (CLAUDE.md:1)

## Description
Codacy's Agentlinter flagged `CLAUDE.md:1` (pattern `Agentlinter_completeness_has-identity`, category Comprehensibility, severity Info): "No identity/persona defined. Without this, the agent has no consistent personality."

## Problem
`CLAUDE.md` and `.github/copilot-instructions.md` are deliberately thin pointers to `AGENTS.md` (the `init-claude` convention) and are meant to stay that way. `AGENTS.md` itself opens directly with "# Project Instructions" and a description of the Tingle repo, without ever stating who the assistant is or what role it plays. The Agentlinter check considers this an incomplete agent-instructions file.

## Expected Behavior
`AGENTS.md` opens with a short identity/persona statement describing the assistant's role for this repo, before the existing "Project Instructions" content. `CLAUDE.md` and `copilot-instructions.md` remain unchanged, thin pointers — Codacy may keep flagging `CLAUDE.md:1` on its own, and that's an accepted tradeoff of the redirect convention.

## Solution
Add a short, generic persona paragraph near the top of `AGENTS.md`, e.g.: "You are an assistant helping maintain Tingle, a personal collection of small, independent utility scripts." Keep it neutral and consistent with the repo's existing self-description; do not duplicate it into `CLAUDE.md` or `copilot-instructions.md`.

## Benefits
Gives the AI assistant clearer, more consistent framing for its role in this repo and satisfies the Codacy Agentlinter completeness check for `AGENTS.md`.
