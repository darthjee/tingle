# Delete the specs folder and the specs.md row

Delete `docs/agents/specs/code_check/` entirely (`git rm -r`; it holds only
`rubycritic/` with README.md, subcommand.md, image.md, config.md, release.md,
file-selection.md). Remove the `code_check rubycritic` row from the Current specs
table in `docs/agents/specs.md`; keep the index and table header, adding a
"None currently." note (or a placeholder row) so the empty table reads clearly.
Ensure no line of `specs.md` still contains the literal `specs/code_check`.

## Files to Change
- `docs/agents/specs/code_check/` — deleted.
- `docs/agents/specs.md` — row removed, empty-state note.
