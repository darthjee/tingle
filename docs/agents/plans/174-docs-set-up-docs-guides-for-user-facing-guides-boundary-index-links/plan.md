# Plan: docs: set up docs/guides/ for user-facing guides (boundary, index, links)

Issue: [174-docs-set-up-docs-guides-for-user-facing-guides-boundary-index-links.md](../../issues/174-docs-set-up-docs-guides-for-user-facing-guides-boundary-index-links.md)

## Overview

Set up `docs/guides/` as the home for end-user guides, one per `tingle`
command. This change creates a new `guide` specialist agent that owns the
folder, relaxes the `AGENTS.md` documentation boundary, and adds a guides
index with placeholder entries. It also links the index from the root
`README.md` and `docs/agents/folder-structure.md`. The per-command guides
themselves are written in #175–#178.

## Agents involved

- [architect](architect.md): root files (`AGENTS.md`, `CLAUDE.md`,
  `README.md`), `.claude/agents/`, and the first version of
  `docs/guides/README.md`. The `guide` agent only exists once this change
  lands, so `architect` writes the first index.
- [product-owner](product-owner.md): `docs/agents/folder-structure.md`.

## Shared contracts

- **Folder:** `docs/guides/`, holding user-facing guides only. Agent docs
  stay in `docs/agents/`.
- **Index file:** `docs/guides/README.md`.
- **Guide file naming:** `docs/guides/<command>.md`, using the command name
  as registered in `commands/*.json`: `install.md`, `linux.md`,
  `kube.md`, `check_file_size.md`.
- **Owning agent:** `guide`, defined in `.claude/agents/guide.md`. Its
  one-line role, used the same way in every file that mentions it: "content
  under `docs/guides/` (end-user guides, one per `tingle` command, and
  the guides index)".
