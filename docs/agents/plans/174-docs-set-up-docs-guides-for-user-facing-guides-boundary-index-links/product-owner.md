# Product-owner Plan: docs: set up docs/guides/ for user-facing guides (boundary, index, links)

Main plan: [plan.md](plan.md)

## Shared contracts

- `docs/guides/` holds end-user guides, one per `tingle` command, plus
  `docs/guides/README.md` as the index. It is owned by the new `guide` agent
  (created by `architect` in this change).
- `docs/agents/` stays agent-facing documentation, owned by you.

## Implementation Steps

### Step 1 — Add docs/guides/ to the folder structure

In `docs/agents/folder-structure.md`'s "Project Root" table, add a
`docs/guides/` row right after the `docs/agents/` row. Describe it as
end-user guides, one per `tingle` command, indexed by
`docs/guides/README.md` and owned by the `guide` agent. If needed, change
the `docs/agents/` row slightly so it clearly reads as agent-facing only.

## Files to Change
- `docs/agents/folder-structure.md` — add the `docs/guides/` row.

## Notes
- Don't create or edit anything under `docs/guides/`; that belongs to
  `architect` (first version) and then `guide`.
