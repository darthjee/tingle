# Update documentation

Both `README.md` and `.claude/agents/cli.md` describe `commands/` as
`commands/*.sh` files "sourced as trusted shell code." Update both to
reflect the new JSON-based, declarative-data format and the new `--help`
contract:

- `README.md`'s folder tree entry, the `tingle` row in the scripts table,
  and the "Commands" section (including the trusted-code security note,
  which changes now that `commands/` holds inert JSON data rather than
  sourced shell code) — this follows the existing convention that `cli`
  keeps `README.md`'s command registration in sync.
- `.claude/agents/cli.md`'s description of `commands/` (`commands/<lang>.sh`
  → `commands/<lang>.json`) — a wording fix only; `cli`'s ownership of
  `commands/` itself is unchanged, so this isn't a scope change requiring
  `architect`.

## Files to Change

- `README.md` — update folder tree, scripts table, and "Commands" section
- `.claude/agents/cli.md` — update `commands/<lang>.sh` references to
  `commands/<lang>.json`
