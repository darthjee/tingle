# Add the update_command row to the specs index
In `docs/agents/specs.md`, replace "No specs in progress." under
**Current specs** with a table (Topic | Specs | Parent issue | Sub-issues),
as the conventions in that file describe, and add one row:
`update_command` | [README](specs/update_command/README.md) | #263 |
#269, #264, #265, #266, #267, #270. #270 removes the row later.

Check that `AGENTS.md` and `CLAUDE.md` need no change. They already link
`docs/agents/specs.md` and use a made-up example path.

## Files to Change
- `docs/agents/specs.md`: add the Current specs table with the
  `update_command` row.
