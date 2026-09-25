# Shell Plan: linux: tab completion does not offer subcommands (shell, sed)

Main plan: [plan.md](plan.md)

## Shared contracts

- **Produces** the linux handler protocol from `plan.md`: `shell/linux/main.sh complete ...` prints `shell sed`, `__tingle_files__`, or nothing.
- **Produces** the hub's handling of the `__tingle_files__` sentinel in `completions/bash/commands.sh`. `completions/` is a root-level folder the architect owns. This change is plain bash, so the shell agent implements it and keeps it minimal.

## Steps

- [01 — Add the file-fallback sentinel to the completion hub](shell/01-hub-file-fallback-sentinel.md)
- [02 — Add shell/linux/completion.sh](shell/02-linux-completion-handler.md)
- [03 — Add the complete flow verb to shell/linux/main.sh](shell/03-linux-main-complete-verb.md)

## Notes
- There is no shell test suite yet (see #229), so test by hand: `source completions/tingle.bash`, then try `tingle linux <TAB>`, `tingle linux s<TAB>`, `tingle linux sed <TAB>` (directories keep a trailing `/`), `tingle linux shell <TAB>` (nothing) and `tingle kube <TAB>` (unchanged). You can also call `shell/linux/main.sh complete ""`, `shell/linux/main.sh complete sed ""` and `shell/linux/main.sh complete shell ""` directly.
- Run `shellcheck` on the touched scripts if it is available.
