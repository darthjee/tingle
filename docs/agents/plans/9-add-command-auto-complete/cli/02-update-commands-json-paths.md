# Update commands/*.json entrypoint paths

Once `python` and `shell` have created their `main.<ext>` entrypoints (shared
contract 2), update the `path` field for each migrated command so
`bin/tingle` (and the completion hub's `tingle resolve`) dispatch to the new
files.

- `commands/python.json`: `check_file_size.path` → `python/check_file_size/main.py`
- `commands/shell.json`: `install.path` → `shell/install/main.sh`

## Files to Change

- `commands/python.json` — `check_file_size.path` updated.
- `commands/shell.json` — `install.path` updated.
