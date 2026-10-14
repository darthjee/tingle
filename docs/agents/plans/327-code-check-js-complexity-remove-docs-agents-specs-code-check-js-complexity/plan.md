# Plan: code_check js_complexity: remove docs/agents/specs/code_check/js_complexity/

Issue: [327-code-check-js-complexity-remove-docs-agents-specs-code-check-js-complexity.md](../../issues/327-code-check-js-complexity-remove-docs-agents-specs-code-check-js-complexity.md)

## Overview
Final cleanup of #315. First, the still-normative content that exists only in
the specs moves into `docs/agents/tingle-js-complexity-image.md`, and the
outdated `js_complexity` paragraph in `docs/agents/architecture.md` is
corrected. Then every reference (code comments, release script, test docstring,
shell agent) is pointed at the image doc. Last, the specs folder and its
`specs.md` row are deleted. Docs and comments only; no behaviour change.
This mirrors #298 (rubycritic).

## Agents involved

- [product-owner](product-owner.md)
- [shell](shell.md)
- [python](python.md)

The architect (coordinator) also owns one edit, listed under
[Architect task](#architect-task).

## Shared contracts

**Order.** product-owner step 01 (move content into the image doc) lands
before anyone repoints, and product-owner step 04 (delete the specs) lands last.

**Target sections in `docs/agents/tingle-js-complexity-image.md`** (the
headings that references point to; GitHub anchors in parentheses):

| Former spec reference | New target |
|---|---|
| `image.md` (whole), `image.md §7` | `## Contract` (`#contract`); key types and per-file states in its new `### Merged JSON` subsection (`#merged-json`) |
| `duplication.md`, `duplication.md §2` | `## Contract` (`#contract`), the jscpd part |
| `details.md`, `details.md §2` | `## Contract` (`#contract`), the escomplex part |
| `sfc.md`, `sfc.md sections 2-4` | `### Single-file components` (`#single-file-components`) |
| `image.md §9`, `duplication.md §6`, `details.md §8`, `sfc.md §7` (smoke-test expectations) | `### Smoke test` (`#smoke-test`) |
| `image.md §13` ("Bumping versions") | `## Bumping versions` (`#bumping-versions`) |

Code comments name the file and the heading in words (e.g.
`docs/agents/tingle-js-complexity-image.md ("Single-file components")`),
never a section number.

**Verification** (run after the last step):

```bash
grep -rn 'specs/code_check/js_complexity' . --exclude-dir=.git \
  | grep -v '^./docs/agents/\(issues\|plans\)/'
```

must print nothing.

## Architect task

- `.claude/agents/shell.md` (lines 26-31): point the version-bump sentence to
  [`docs/agents/tingle-js-complexity-image.md`](../../docs/agents/tingle-js-complexity-image.md#bumping-versions)
  ("Bumping versions") and drop the outdated "(moving to
  `docs/agents/tingle-js-complexity-image.md` in #319)" note.

## Notes
- `docs/agents/specs/code_check/` only holds `js_complexity/`, so it is
  deleted too.
- Historical and process content (merge order, the grounding run in
  `image.md §10`, the release ordering rule in `release.md §1`) is dropped,
  not moved.
