# Plan: code_check rubycritic: remove docs/agents/specs/code_check/rubycritic/

Issue: [298-code-check-rubycritic-remove-docs-agents-specs-code-check-rubycritic.md](../../issues/298-code-check-rubycritic-remove-docs-agents-specs-code-check-rubycritic.md)

## Overview
Final cleanup of #290. Move the still-normative RubyCritic JSON contract
(`subcommand.md` §5) into the permanent `docs/agents/tingle-rubycritic-image.md`,
repoint every link and code comment that cites the temporary specs to sections of
that permanent doc, then delete `docs/agents/specs/code_check/` and its row in
`docs/agents/specs.md`. The architect repoints `.claude/agents/shell.md` itself
(root-level agent definition, architect scope).

## Agents involved

- [product-owner](product-owner.md)
- [shell](shell.md)
- [python](python.md)

## Shared contracts

Target sections in `docs/agents/tingle-rubycritic-image.md` that every repointed
reference must use (anchors are GitHub-generated from the headings):

| Old citation | New target | Anchor |
|---|---|---|
| `image.md` §4 (entrypoint contract) | `## Contract` (existing) | `#contract` |
| `image.md` §6 (smoke-test fixture) | `### Smoke test` (existing, under Release pipeline) | `#smoke-test` |
| `image.md` §8 (bumping versions) | `## Bumping versions` (existing) | `#bumping-versions` |
| `subcommand.md` §5 (RubyCritic JSON contract) | `## RubyCritic JSON contract` (NEW, added by product-owner, placed right after `## Contract`) | `#rubycritic-json-contract` |

Code comments use the plain path form, e.g.
`docs/agents/tingle-rubycritic-image.md ("Bumping versions")` — matching the
existing precedent in `shell/linux/Dockerfile:25`.

Architect's own change: `.claude/agents/shell.md:21-22` — replace
"follow section 8 of `docs/agents/specs/code_check/rubycritic/image.md`" with
"follow the \"Bumping versions\" section of
[`docs/agents/tingle-rubycritic-image.md`](../../docs/agents/tingle-rubycritic-image.md#bumping-versions)".

Final verification (architect, after all agents): `grep -rn 'specs/code_check' . --exclude-dir=.git`
matches only `docs/agents/issues/`, `docs/agents/plans/` and `.claude/state/` files.
