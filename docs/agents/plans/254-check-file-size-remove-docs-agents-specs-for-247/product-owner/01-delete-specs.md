# Delete the check_file_size specs
Remove the whole `docs/agents/specs/check_file_size/` folder with `git rm -r`. It holds `README.md`, `config.md`, `exclude.md`, `gitignore.md`, `ignore-include.md` and `min-level.md`. If `docs/agents/specs/` is then empty, it disappears too, since git doesn't track empty folders. Don't add a `.gitkeep`: the index already explains the layout.

## Files to Change
- `docs/agents/specs/check_file_size/` — deleted.
