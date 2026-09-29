# Cli Plan: update: support updating git-clone installs (git pull)

Main plan: [plan.md](plan.md)

## Shared contracts

This agent relies on the shell agent's behavior, described in the table in [plan.md](plan.md#shared-contracts). The help text must describe it accurately, but it does not need to quote every message.

## Implementation Steps

### Step 1 — Update the `update` help text
In `commands/shell.json`:
- Change `short_help` to cover both kinds, for example "Update tingle: a web install to the latest or a pinned release, a git checkout with git pull."
- In `long_help`, replace the final "A git checkout of tingle is not updated by this command…" paragraph with a "Git checkouts" paragraph. It should say that the command runs `git pull --ff-only` on the current branch, then re-runs `tingle install`. It should explain that the command refuses a dirty tree (tracked changes), a detached HEAD, a branch with no upstream, or a diverged branch, and changes nothing in those cases. It should say that `--check` fetches and reports how many commits the branch is behind and ahead of its upstream, that a version pin and `--force` are refused, and that there is no confirmation prompt.
- Scope the confirmation/`TINGLE_ASSUME_YES` sentence and the opening "Updates a web install…" sentence to web installs.

### Step 2 — Check the README scripts table
If the README's `update` row says "web install" only, align it with the new `short_help`.

## Files to Change
- `commands/shell.json` — `update.short_help` and `update.long_help`.
- `README.md` — the `update` row in the scripts table, if needed.

## Notes
- Keep `commands/shell.json` valid JSON (`jq empty commands/shell.json`), and check the result with `bin/tingle update --help`.
