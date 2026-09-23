# Architect Plan: docs: set up docs/guides/ for user-facing guides (boundary, index, links)

Main plan: [plan.md](plan.md)

## Shared contracts

- You create `.claude/agents/guide.md` (agent name `guide`), scoped to
  `docs/guides/`.
- You create `docs/guides/README.md` with a placeholder for each guide file
  `docs/guides/<command>.md` (`install`, `linux`, `kube`, `check_file_size`).
- `product-owner` separately adds `docs/guides/` (owner `guide`) to
  `docs/agents/folder-structure.md`. Use the same one-line role wording for
  `guide` everywhere.

## Steps

- [01 — Create the guide agent](architect/01-create-guide-agent.md)
- [02 — Update AGENTS.md](architect/02-update-agents-md.md)
- [03 — Update CLAUDE.md](architect/03-update-claude-md.md)
- [04 — Create the guides index](architect/04-create-guides-index.md)
- [05 — Point the root README to the guides](architect/05-update-root-readme.md)

## Notes

- Check `.github/copilot-instructions.md`. If it mirrors the `CLAUDE.md`
  Documentation summary, add the same `docs/guides/` mention there.
- CI lint covers the script folders only. There is no Markdown lint job,
  so check the new links by hand.
