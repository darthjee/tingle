# Move the RubyCritic JSON contract into the image doc

Copy `docs/agents/specs/code_check/rubycritic/subcommand.md` §5 ("RubyCritic JSON
contract", lines ~173-326: intro, sample JSON, "Fields used" table, Checks,
"JSON booleans are not numbers here", Path mapping, "Per-method details
(`--details [N]`, #291)") into a new `## RubyCritic JSON contract` section of
`docs/agents/tingle-rubycritic-image.md`, placed right after `## Contract`.
Demote inner headings so they nest under it.

Rewrite intra-spec cross references: `[image.md](image.md#4-entrypoint-contract)`
and "(section 4)" become links to `#contract` in the same doc; the
`[section 10](#10-messages)` link is dropped or replaced with a plain mention
that the messages live in the code (`python/.../code_check/rubycritic/`).

Then:
- Repoint the Contract bullet at lines ~137-139 (currently linking
  `specs/code_check/rubycritic/subcommand.md#5-rubycritic-json-contract`) to
  `#rubycritic-json-contract`.
- In `## Bumping versions` step 3 (~lines 319-323), replace "the subcommand spec,
  or this doc once the specs are removed" with a link to
  `#rubycritic-json-contract`.

## Files to Change
- `docs/agents/tingle-rubycritic-image.md` — new section, repointed link, updated bump note.
