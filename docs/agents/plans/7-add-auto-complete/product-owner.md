# Product-Owner Plan: Add Auto Complete

Main plan: [plan.md](plan.md)

## Shared contracts

`shell` is creating a new top-level folder, `completions/`, containing `completions/tingle.bash` — the bash completion script for `tingle`, sourced from `~/.bashrc` by `tingle install`. Document it with this exact path and purpose.

## Implementation Steps

### Step 1 — Document the new `completions/` folder

Add `completions/` as a new top-level folder in the project's structure documentation, consistent with how `bin/`, `shell/`, `python/`, and `node/` are already documented.

## Files to Change

- `docs/agents/architecture.md` — add a `### completions/` subsection under "Source Code Layout" describing it as holding the bash completion script(s) for `tingle`, sourced from `~/.bashrc` by `tingle install`.
- `docs/agents/folder-structure.md` — add a `completions/` row to the "Project Root" table with the same description.

## Notes

- Scoped purely to documentation; no code changes. Coordinate with `shell.md` only on the exact folder/file name (`completions/tingle.bash`), already fixed above.
