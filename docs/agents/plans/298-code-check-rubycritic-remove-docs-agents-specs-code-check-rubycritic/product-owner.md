# Product-owner Plan: code_check rubycritic: remove docs/agents/specs/code_check/rubycritic/

Main plan: [plan.md](plan.md)

## Shared contracts

You must produce the new section `## RubyCritic JSON contract` (anchor
`#rubycritic-json-contract`) in `docs/agents/tingle-rubycritic-image.md`,
placed right after `## Contract`. The `shell` and `python` agents point their
comments at it and at the existing `#contract`, `#smoke-test` and
`#bumping-versions` sections — do not rename those headings.

## Steps

- [01 — Move the RubyCritic JSON contract into the image doc](product-owner/01-move-json-contract.md)
- [02 — Drop the spec link from architecture.md](product-owner/02-architecture-link.md)
- [03 — Delete the specs folder and the specs.md row](product-owner/03-delete-specs.md)

## Notes
- Do not edit `.claude/agents/shell.md` (architect), code comments under
  `docker/`/`scripts/` (shell) or `python/tests/` (python).
- `docs/agents/specs.md` lines 14 and 30 use `code_check/rubycritic/` only as a
  layout example (no link); they may stay, but must not contain the literal
  string `specs/code_check`.
- No CI job lints Markdown; verify links by hand.
