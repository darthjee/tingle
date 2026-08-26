# Plan: Add Auto Complete

Issue: [7-add-auto-complete.md](../../issues/7-add-auto-complete.md)

## Overview

Add a bash completion script (`completions/tingle.bash`) that completes `tingle` command names from `commands/*.json`, plus a new `tingle install` command (dispatched like any other command) that idempotently wires `PATH` and the completion script into the user's `~/.bashrc`. `completions/` is a new top-level folder, so the project's architecture/folder-structure docs need updating alongside the implementation.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- New top-level folder: `completions/`, containing a single file `completions/tingle.bash` — the bash completion script for `tingle`.
- Folder purpose (for docs): "Bash completion script(s) for `tingle`, sourced from `~/.bashrc` by `tingle install`."
- `shell` creates the folder/file and documents its own script header; `product-owner` documents the folder itself in `docs/agents/architecture.md` and `docs/agents/folder-structure.md`, using the exact name `completions/` and the purpose line above.
