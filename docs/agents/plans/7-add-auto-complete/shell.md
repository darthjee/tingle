# Shell Plan: Add Auto Complete

Main plan: [plan.md](plan.md)

## Shared contracts

Owns the new top-level folder `completions/`: create `completions/tingle.bash` — the bash completion script for `tingle`, sourced from `~/.bashrc` by `tingle install`. `product-owner` documents this folder in the architecture docs using this exact path and purpose.

## Steps

- [01 — Add install command mapping](shell/01-add-install-command-mapping.md)
- [02 — Implement tingle install](shell/02-implement-tingle-install.md)
- [03 — Implement bash completion script](shell/03-implement-bash-completion-script.md)
- [04 — Update README](shell/04-update-readme.md)

## Notes

- `bin/tingle` requires no changes: `install` dispatches through `commands/shell.json` exactly like every other command, and `help`/`--help` are already implemented and must keep working unchanged.
- The completion script must replicate `bin/tingle`'s existing command-resolution rule: files are loaded in alphabetical order (`node.json`, `python.json`, `shell.json`) and the first file to define a given command name wins. Completing a name `bin/tingle` would resolve to a different file's entry would be a bug.
