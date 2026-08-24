# cli Plan: Add help system and migrate command mappings from sourced .sh to JSON

Main plan: [plan.md](plan.md)

## Steps

- [01 — Migrate command mappings to JSON](cli/01-migrate-commands-to-json.md)
- [02 — Rewrite bin/tingle's help system](cli/02-rewrite-bin-tingle-help-system.md)
- [03 — Update documentation](cli/03-update-documentation.md)

## Notes

- `jq` is a new hard dependency for `bin/tingle` — confirmed acceptable by
  the issue owner, who has it installed. No dependency-free fallback is
  needed.
- Only one command is registered today (`check_file_size`), so the JSON
  migration carries no real data-migration risk.
- No CI config exists in this repo, so there is no `## CI Checks` section
  to add.
