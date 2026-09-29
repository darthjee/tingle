# Product-owner Plan: check_file_size: remove docs/agents/specs/ for #247

Main plan: [plan.md](plan.md)

## Shared contracts

- Start only after the `guide` agent has finished its coverage check.
- Afterwards, no tracked file may reference `docs/agents/specs/check_file_size/`.

## Steps

- [01 — Delete the check_file_size specs](product-owner/01-delete-specs.md)
- [02 — Update the specs index](product-owner/02-update-specs-index.md)
- [03 — Replace the AGENTS.md example](product-owner/03-agents-md-example.md)

## CI Checks
- Docs: the `lint` job in `.circleci/config.yml`.
- Run `git grep -n "specs/check_file_size"`. It should return nothing.

## Notes
- Keep `docs/agents/specs.md` and its links in `AGENTS.md` and `CLAUDE.md`. The index is permanent.
- Untracked files under `docs/agents/issues/` may still mention the old paths. They're local drafts, so ignore them.
