# Migrate command mappings to JSON

Replace the sourced `commands/*.sh` mapping files with declarative
`commands/*.json` files, one per language, mirroring the current naming.
This is a hard cutover — the `.sh` files are deleted in this same step,
with no coexistence/fallback period.

Each JSON file is a flat object keyed by command name, mapping to
`{"path": ..., "short_help": ..., "long_help": ...}` (path relative to the
repo root, same as today's `.sh` values). Only `check_file_size` is
registered today; carry its metadata over from its script's own docstring
(`python/check_file_size.py`) rather than inventing new wording. The
`node.json` and `shell.json` files start out as empty JSON objects (`{}`),
same as today's empty `.sh` files.

## Files to Change

- `commands/python.sh` — delete
- `commands/node.sh` — delete
- `commands/shell.sh` — delete
- `commands/python.json` — create, with the `check_file_size` entry:
  `{"path": "python/check_file_size.py", "short_help": "...", "long_help": "..."}`
- `commands/node.json` — create, `{}`
- `commands/shell.json` — create, `{}`
