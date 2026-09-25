# Product-owner Plan: linux: tab completion does not offer subcommands (shell, sed)

Main plan: [plan.md](plan.md)

## Shared contracts

- **Documents** the `__tingle_files__` file-fallback sentinel exactly as `plan.md` defines it. The exact string matters.
- **Relies on** `shell/linux/completion.sh` existing, so linux now has a completion handler.

## Implementation Steps

### Step 1 — Document the sentinel in the completion contract
In `docs/agents/architecture.md`, in the flow-verb / completion bullets (around "Completion is opt-in per command"), add a bullet: a handler that prints exactly `__tingle_files__` gets the hub's native file/folder completion, the same as a command with no handler. Empty output means no suggestions. In the `completions/` section, mention the sentinel in the `completions/bash/commands.sh` bullet. Don't list `linux` among commands without a handler.

### Step 2 — Keep folder-structure in sync
In `docs/agents/folder-structure.md`, extend the `completions/` row's description of `commands.sh` to mention the sentinel fallback. If a `shell/` row lists per-command files, add `completion.sh` for linux.

## Files to Change
- `docs/agents/architecture.md` — sentinel in the completion contract and the `completions/` section.
- `docs/agents/folder-structure.md` — sentinel in the `completions/` row, and linux `completion.sh` if files are listed.
