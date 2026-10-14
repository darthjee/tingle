# Check the guide covers the user-facing specs
`subcommand.md`, `file-selection.md`, `config.md` and the user-facing parts
of `duplication.md`, `details.md` and `sfc.md` describe flags, config keys,
defaults, report columns and exit codes. Check each against
`docs/guides/code_check/js_complexity.md` and
`docs/agents/architecture.md`. If a normative user-facing rule is missing,
ask the `guide` agent to add it to the guide (the guide is not yours to
edit), or add it to `docs/agents/` when it is agent-facing. Usually nothing
is missing: #320-#326 updated the guide as they went.

## Files to Change
- None expected. If something is missing: `docs/guides/code_check/js_complexity.md` (via `guide`) or `docs/agents/architecture.md`.
