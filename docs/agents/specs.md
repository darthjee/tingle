# Specs

Specs are **temporary, feature-level design documents** for a split issue
(a parent GitHub issue broken into several sub-issues). They describe the
user-visible behaviour and the key technical decisions, so each sub-issue can
be implemented against one agreed contract.

This index is permanent. The specs it lists are not.

## Layout

Specs live under `docs/agents/specs/<topic>/` while the sub-issues are in
progress. A topic may also be a nested `<command>/<subcommand>/` folder (e.g.
`code_check/rubycritic/`), so that sibling subcommands of the same command can
get their own spec sets:

- `README.md` — the shared contracts: overview, feature list and sub-issues,
  merge order, and anything every feature must agree on (flag names, config
  keys, precedence, exit codes, ...).
- One file per feature (e.g. `ignore-include.md`), readable on its own.

Once the user guide (`docs/guides/`) and the code cover everything, the
split's final cleanup sub-issue removes the `docs/agents/specs/<topic>/`
folder.

## Conventions

- The folder name is the command or topic (e.g. `code_check`). For a split
  that covers one subcommand, the folder is nested as
  `<command>/<subcommand>/` (e.g. `code_check/rubycritic/`), and the cleanup
  sub-issue removes only that subcommand folder (plus the command folder when
  it becomes empty).
- The `README.md` links the parent GitHub issue, and each feature spec links
  its sub-issue.
- A new split adds an entry to [Current specs](#current-specs) (a table with
  Topic, Specs, Parent issue and Sub-issues columns), and its cleanup
  sub-issue removes the entry.
- Specs are normative: write "must" / "is", not "could" / "might".

## Current specs

| Topic | Specs | Parent issue | Sub-issues |
|---|---|---|---|

None currently.
