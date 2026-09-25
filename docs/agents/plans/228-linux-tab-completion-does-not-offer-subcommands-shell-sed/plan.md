# Plan: linux: tab completion does not offer subcommands (shell, sed)

Issue: [228-linux-tab-completion-does-not-offer-subcommands-shell-sed.md](../../issues/228-linux-tab-completion-does-not-offer-subcommands-shell-sed.md)

## Overview
Add a bash completion handler for `tingle linux` (`shell/linux/completion.sh` plus a `complete` flow verb in `shell/linux/main.sh`). Then `tingle linux <TAB>` offers `shell` and `sed`. Also teach the level-two hub (`completions/bash/commands.sh`) one reserved sentinel word. A handler prints it to ask for the hub's native file/folder completion, which `tingle linux sed <TAB>` needs. Docs are updated for agents and end users.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)
- [guide](guide.md)

## Shared contracts

- **File-fallback sentinel:** the exact string `__tingle_files__`.
  - When a handler's whole stdout, with surrounding whitespace trimmed, equals `__tingle_files__`, `completions/bash/commands.sh` runs `COMPREPLY=($(compgen -f -- "$cur"))` and `compopt -o filenames 2>/dev/null || true`. That is the same fallback it uses for commands with no `completion.<ext>`.
  - Any other output, including empty output, still goes through `compgen -W "<output>" -- "$cur"` as it does today. Empty output means no suggestions.
- **Linux handler protocol:** `main.sh complete <argv...>` receives raw argv from the subcommand onward. The last element is the word being typed and may be empty.
  - Committed words = argv minus the last element.
  - No committed words: print `shell sed`.
  - First committed word is `sed`: print `__tingle_files__`.
  - First committed word is `shell`, or anything else: print nothing.
  - Always exit 0. Never start Docker.
