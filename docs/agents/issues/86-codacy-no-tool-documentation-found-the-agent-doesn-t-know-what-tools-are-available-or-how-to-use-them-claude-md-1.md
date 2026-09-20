# Issue: Codacy: No tool documentation found. The agent doesn't know what tools are available or how to use them. (CLAUDE.md:1)

## Description
Codacy's Agentlinter flagged `CLAUDE.md:1` (pattern `Agentlinter_completeness_has-tools`, category Documentation, severity Info, Codacy issue ID `d901ace01a8ca8607dd8cf54bcb9fe22`): "No tool documentation found. The agent doesn't know what tools are available or how to use them."

## Problem
Neither `CLAUDE.md` nor `AGENTS.md` says which tools an agent can use in this repo or how to invoke them. The specialist agents defined under `.claude/agents/` (architect, cli, node, product-owner, python, shell) are never mentioned in the agent-instructions files. `CLAUDE.md` is a thin pointer to `AGENTS.md`, the single source of truth.

## Expected Behavior
`AGENTS.md` has a short **Tools** section listing the specialist agents available in the repo and what each one is for, so an agent knows which specialist to delegate to. `CLAUDE.md` stays unchanged, a thin pointer — Codacy may keep flagging `CLAUDE.md:1` on its own, an accepted tradeoff of the redirect convention (same as #89).

## Solution
Add a `## Tools` section to `AGENTS.md`, following the approach used for #89, listing the specialist agents in `.claude/agents/` with a one-line role each:
- `architect` — cross-cutting tasks, multi-agent coordination, root-level files.
- `cli` — entry points under `bin/` (arg parsing, `--help`, exit codes, dispatch).
- `node` — Node.js scripts under `node/`.
- `python` — Python scripts under `python/`.
- `shell` — Bash/Shell scripts under `shell/`.
- `product-owner` — content under `docs/agents/` (architecture, flow, folder structure, contributing, issues, plans).

Point to `.claude/agents/` as the source for the full descriptions rather than duplicating them. Other tooling (test/lint commands, the `bin/tingle` CLI, release scripts) is out of scope for this issue. Do not modify `CLAUDE.md` or `.github/copilot-instructions.md`.

## Benefits
Gives the AI assistant an explicit, discoverable list of the tools (specialist agents) available and when to use each, and satisfies the Codacy Agentlinter completeness check for `AGENTS.md`.
