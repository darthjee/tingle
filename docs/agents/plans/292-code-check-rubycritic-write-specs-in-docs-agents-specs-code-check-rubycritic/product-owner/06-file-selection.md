# Write file-selection.md (#296)
Create `docs/agents/specs/code_check/rubycritic/file-selection.md`, linking #296 at the top. Mirror `file_size`'s behaviour in `python/code_check/file_size/file_collector.py` and `git_ignore.py`.

It must specify:
- **Default excludes:** the full list.
- **`--exclude <dir>`:** additive, repeatable or comma-separated to match `file_size`. `--no-default-excludes` drops the defaults.
- **`--ignore <glob>` / `--include <glob>`:** repeatable, matched against the path relative to `<path>`. `--include` combines with the fixed `.rb` filter.
- **`.gitignore`:** respected by default when `<path>` is inside a git repo, and skipped silently when git or a repo isn't available. `--no-gitignore` turns it off.
- **Symlinks:** those pointing outside `<path>` are skipped. State whether `file_size` already does this, and align with it.
- **Filter order:** the exact order, and whether `FileCollector` is reused directly or through a shared helper. Point out what `file_size` has that doesn't apply here, e.g. the binary check and `--ext`.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/file-selection.md`: new.
