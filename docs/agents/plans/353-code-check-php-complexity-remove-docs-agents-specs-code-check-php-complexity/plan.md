# Plan: code_check php_complexity: remove docs/agents/specs/code_check/php_complexity/

Issue: [353-code-check-php-complexity-remove-docs-agents-specs-code-check-php-complexity.md](../../issues/353-code-check-php-complexity-remove-docs-agents-specs-code-check-php-complexity.md)

## Overview

Final cleanup of the #344 split, mirroring the RubyCritic cleanup (#298).
First, product-owner audits the eight spec files and moves anything still
needed into the permanent docs. Then every remaining link to
`docs/agents/specs/code_check/php_complexity/` (docs, agent file, code comments)
is repointed, and the spec folder plus its `specs.md` row are deleted. No
behaviour changes. In code files, only comments change.

## Agents involved

- [product-owner](product-owner.md): audit and migrate, repoint `architecture.md`, delete specs and index row
- [shell](shell.md): repoint comments in `docker/php_complexity/` and `scripts/release_image.sh`
- [python](python.md): repoint the docstring in `python/tests/code_check/php_complexity/sample_output.py`
- [architect](architect.md): repoint `.claude/agents/shell.md`

## Shared contracts

Link targets that replace the spec references (all in
`docs/agents/tingle-php-complexity-image.md`; headings already exist):

| Old spec reference | New target |
|---|---|
| `image.md` §7 Merged JSON | `tingle-php-complexity-image.md#merged-json` |
| `image.md` §9 Smoke-test fixture | `tingle-php-complexity-image.md#smoke-test` |
| `image.md` §13 Bumping versions | `tingle-php-complexity-image.md#bumping-versions` |
| `image.md` + `duplication.md` (entrypoint contract) | `tingle-php-complexity-image.md#contract` (+ `#merged-json`) |
| `cli.md`, `config.md`, `selection.md` (from `architecture.md`) | `docs/guides/code_check/php_complexity.md` (user-visible behaviour) or dropped, keeping the existing `tingle-php-complexity-image.md` link |

product-owner must keep these four headings (`Contract`, `Merged JSON`,
`Smoke test`, `Bumping versions`) stable while migrating content, so the
other agents' links resolve.

Merge order: product-owner's audit/migration lands before (or with) the
deletion. The other agents' repoints are independent and only need the
anchors above.

## Acceptance check

```bash
grep -rn 'specs/code_check/php_complexity' . --exclude-dir=.git \
  | grep -v 'docs/agents/issues/\|docs/agents/plans/'
```

must print nothing, and `docs/agents/specs/code_check/` must no longer exist.
