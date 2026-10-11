# Plan: Add an `examples` specialist agent owning the top-level `examples/` folder

Issue: [312-add-an-examples-specialist-agent-owning-the-top-level-examples-folder.md](../../issues/312-add-an-examples-specialist-agent-owning-the-top-level-examples-folder.md)

## Overview

Add a new `examples` specialist agent (`.claude/agents/examples.md`) that owns
the top-level `examples/` folder of shipped, terminal-printed walkthroughs,
and register it everywhere the agent roster and folder layout are documented.
Documentation/configuration only — no code changes.

## Context

`examples/` is introduced by #311 (first file: `examples/kube/end_to_end.txt`,
printed by `tingle kube example`) and ships in the release zip. None of the
existing agents fits it: `guide` owns repository-only `docs/guides/`, the
language agents own code, and `architect` owns coordination and root-level
files.

## Steps

- [01 — Create the examples agent file](plan/01-create-examples-agent.md)
- [02 — Register the agent in the root-level rosters](plan/02-register-agent-in-rosters.md)
- [03 — Document examples/ in the folder structure](plan/03-document-folder-structure.md)

## Notes

- Ownership: steps 01 and 02 touch `.claude/agents/` and root-level files
  (`AGENTS.md`, `CLAUDE.md`), which belong to `architect`; step 03 touches
  `docs/agents/folder-structure.md`, which belongs to `product-owner`.
- Out of scope (owned by #311): creating `examples/` content, packaging it
  into the release zip, and the code that prints the files.
- No CI job covers these Markdown files; verify by reading the rendered
  files and checking that every roster lists the same eight agents.
