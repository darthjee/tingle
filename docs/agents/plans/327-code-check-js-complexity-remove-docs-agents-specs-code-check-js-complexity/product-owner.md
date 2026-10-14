# Product-owner Plan: code_check js_complexity: remove docs/agents/specs/code_check/js_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

- You produce the target sections listed in [plan.md](plan.md#shared-contracts),
  in particular a new `### Merged JSON` subsection inside `## Contract` of
  `docs/agents/tingle-js-complexity-image.md`. Keep the existing headings
  `## Contract`, `### Single-file components`, `### Smoke test` and
  `## Bumping versions` unchanged: shell, python and the architect point to them.
- Step 01 lands first. Step 04 (deleting the specs) lands last, after the shell,
  python and architect repoints.

## Steps

- [01 — Move the remaining contract into the image doc](product-owner/01-move-contract-into-image-doc.md)
- [02 — Fix the outdated js_complexity section in architecture.md](product-owner/02-fix-architecture-js-complexity.md)
- [03 — Check the guide covers the user-facing specs](product-owner/03-check-guide-coverage.md)
- [04 — Delete the specs and their index row](product-owner/04-delete-specs.md)

## CI Checks
- None specific to `docs/` (the CircleCI `lint` job runs `ruff` on Python only).
  Run the verification grep from [plan.md](plan.md#shared-contracts).

## Notes
- Write the moved content as the current contract: no "from #324", "`null`
  before #325", "#318 emits ..." history.
- Normative style: "must" / "is".
