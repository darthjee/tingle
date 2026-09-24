# Cli Plan: install: handle moved repo, add uninstall, and clarify non-bash shells

Main plan: [plan.md](plan.md)

## Shared contracts

- Relies on `shell/uninstall/main.sh` (flow verb `run`, no options) being
  provided by the shell agent.
- Help text must match the behavior and scope in
  [plan.md](plan.md#shared-contracts): moved-repo rewrite, uninstall leaves the
  folder in place, bash only.

## Implementation Steps

### Step 1 — Register `uninstall` and update `install` help
In `commands/shell.json`:
- Add an `uninstall` entry:
  - `path`: `shell/uninstall/main.sh`
  - `short_help`: "Remove tingle's PATH and bash completion wiring from ~/.bashrc."
  - `long_help`: says it removes only the marker block, leaves the rest of
    `~/.bashrc` untouched, does not delete the tingle folder, is safe to
    re-run, and includes the usage line.
- Update `install`'s `long_help`:
  - Re-running after the tingle folder moved rewrites the existing block to
    the new path.
  - Only bash (`~/.bashrc`) is supported. zsh and fish are not wired.
  - On macOS, `~/.bash_profile` must source `~/.bashrc`.
  - Point to `tingle uninstall`.

Command completion reads `commands/*.json`, so `uninstall` shows up there
automatically. No change to `completions/` is needed.

## Files to Change
- `commands/shell.json` — new `uninstall` entry; updated `install.long_help`.

## Notes
- Check that the JSON is still valid with `jq empty commands/shell.json`.
- Check that `tingle --help uninstall` and `tingle` (the command list) show it.
