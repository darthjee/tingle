# Product-owner Plan: code_check php_complexity: remove docs/agents/specs/code_check/php_complexity/

Main plan: [plan.md](plan.md)

## Shared contracts

Keep the headings `## Contract`, `### Merged JSON`, `### Smoke test` and
`## Bumping versions` in `docs/agents/tingle-php-complexity-image.md` (anchors
`#contract`, `#merged-json`, `#smoke-test`, `#bumping-versions`). The shell,
python and architect repoints link to them.

## Implementation Steps

### Step 1 — Audit the specs and migrate what is still needed

Read each spec file under `docs/agents/specs/code_check/php_complexity/`
(`README.md`, `cli.md`, `config.md`, `details.md`, `duplication.md`,
`image.md`, `release.md`, `selection.md`) and compare it with:

- `docs/agents/tingle-php-complexity-image.md`: the image contract. It already has
  Contract, Merged JSON (incl. `duplication` / `jscpd`), Release pipeline,
  Smoke test, CircleCI, Local build and Bumping versions. Check
  especially `image.md` §5 parse check / staged tree, §6 PDepend failure and
  parse errors, §7 XML→JSON mapping, §8 exit status / encoding, §9.1
  fixture contents, §11 runtime environment, and `duplication.md` §2–§5
  (jscpd invocation, per-file duplicated lines, failure handling).
- `docs/agents/architecture.md`: CLI/config/selection design of
  `python/code_check/php_complexity/`.
- `docs/guides/code_check/php_complexity.md`: user-visible behaviour (owned by
  the `guide` agent; if something user-visible is missing, note it in the
  PR rather than editing the guide, unless the gap is clear and small).

Move only normative facts an implementer or maintainer still needs. Skip
historical material: sub-issue lists, merge order, the grounding run (§10),
and "#34x adds …" phrasing. Write it in the permanent docs' present-tense
style.

### Step 2 — Repoint `architecture.md` and delete the specs

- `docs/agents/architecture.md` (around lines 295, 326 and 348): replace the
  links to `specs/code_check/php_complexity/cli.md`, `config.md` and
  `selection.md`. "The normative contract is …cli.md" becomes a pointer to
  the user guide `../guides/code_check/php_complexity.md`. Drop the
  "; see …config.md" and "See …selection.md" tails (or point them to the
  guide's matching sections), as #298 did for RubyCritic.
- `docs/agents/specs.md`: remove the `code_check/php_complexity` row from
  *Current specs*, keeping the heading and the empty table header.
- Delete `docs/agents/specs/code_check/php_complexity/` and the then-empty
  `docs/agents/specs/code_check/` (`git rm -r`).

## Files to Change

- `docs/agents/tingle-php-complexity-image.md`: absorb any still-needed spec content
- `docs/agents/architecture.md`: repoint the three spec links
- `docs/agents/specs.md`: drop the `code_check/php_complexity` row
- `docs/agents/specs/code_check/`: deleted

## CI Checks

- Markdown: `markdownlint` per `.markdownlint.json` (CI lint job)

## Notes

- Do not edit historical files under `docs/agents/issues/` or `docs/agents/plans/`.
- Precedent: commit 6f84b0b (#298), where product-owner moved the RubyCritic JSON
  contract into its image doc and dropped the spec link from `architecture.md`.
