# Implement tingle install

Write `shell/install.sh`, the implementation behind the `install` command registered in step 01. It must be idempotent and must only ever append to `~/.bashrc`, never overwrite it.

Behavior:

- Resolve the repo root the same way `bin/tingle` does (`cd "$(dirname "$0")/.." && pwd`, adjusted for this script's own location), so the emitted lines work regardless of where the repo is checked out.
- Add `tingle` to `PATH` via `~/.bashrc`: append an `export PATH="<repo>/bin:$PATH"` line (or equivalent), guarded by a marker comment pair, e.g. `# >>> tingle >>>` / `# <<< tingle <<<`.
- Add a line sourcing `completions/tingle.bash` (absolute path, from the resolved repo root) via `~/.bashrc`, inside the same marker block.
- Idempotency: before appending, check whether the marker block already exists in `~/.bashrc` (e.g. `grep -qF '# >>> tingle >>>' ~/.bashrc`) and skip appending if so — running `tingle install` twice must not duplicate lines.
- If `~/.bashrc` does not exist, create it (e.g. `touch`) before appending.
- Must not disturb any unrelated existing content in `~/.bashrc` — only ever append the tingle marker block; never search-and-replace or truncate.

## Files to Change

- `shell/install.sh` — new script implementing the behavior above; include the usual header comment documenting usage/dependencies (per project convention).
