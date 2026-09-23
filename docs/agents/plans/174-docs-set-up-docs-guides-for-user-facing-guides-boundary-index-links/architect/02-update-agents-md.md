# Update AGENTS.md

- **Boundaries:** replace "or documentation outside `docs/agents/`" with a
  rule that puts user-facing guides in `docs/guides/` and agent-facing docs
  in `docs/agents/`, and forbids documentation anywhere else.
- **Boundaries:** add "**Must**: update the matching guide in
  `docs/guides/` whenever a command's behaviour changes."
- **Tools:** add `guide` to the agent roster: "content under
  `docs/guides/` (end-user guides, one per `tingle` command, and the guides
  index)".
- **Documentation:** change the intro line so it no longer says *all*
  documentation lives under `docs/agents/`. Add a row for
  [User Guides](docs/guides/README.md), or add a short
  "User guides (`docs/guides/`)" subsection.
- Bump `Last updated` to the implementation date.

## Files to Change
- `AGENTS.md` — boundary, new Must rule, roster entry, documentation index,
  `Last updated`.
