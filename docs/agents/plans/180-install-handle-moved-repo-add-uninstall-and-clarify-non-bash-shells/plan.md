# Plan: install: handle moved repo, add uninstall, and clarify non-bash shells

Issue: [180-install-handle-moved-repo-add-uninstall-and-clarify-non-bash-shells.md](../../issues/180-install-handle-moved-repo-add-uninstall-and-clarify-non-bash-shells.md)

## Overview
`tingle install` learns to notice when the tingle folder has moved. When the
path in the `~/.bashrc` marker block no longer matches, it rewrites that block
in place. A new `tingle uninstall` command removes the marker block and leaves
the tingle folder alone. Bash-only support is kept on purpose and is now written
down in the help text and the user guides.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- **Marker block** (unchanged shape, written by install, parsed by install and uninstall):
  ```
  # >>> tingle >>>
  export PATH="<TINGLE_FOLDER>/bin:$PATH"
  source "<TINGLE_FOLDER>/completions/tingle.bash"
  # <<< tingle <<<
  ```
  `<TINGLE_FOLDER>` is the absolute tingle root. The installed path is the
  `<TINGLE_FOLDER>` taken from the `export PATH=` line inside the block.
- **Entry point:** `shell/uninstall/main.sh`, using the same flow-verb protocol
  as `shell/install/main.sh` (`main.sh run [args...]` → `executor.sh`).
  It takes no options.
- **Messages** (`<BASHRC>` is the absolute path, e.g. `/home/you/.bashrc`):
  - install, fresh: `tingle installed. Run 'source <BASHRC>' or restart your shell to start using it.` (unchanged)
  - install, same path: `tingle is already installed in <BASHRC>` (unchanged)
  - install, different path: `tingle install updated in <BASHRC> (now pointing to <TINGLE_FOLDER>). Run 'source <BASHRC>' or restart your shell to pick it up.`
  - uninstall, removed: `tingle uninstalled from <BASHRC>. Restart your shell to drop it from PATH. The tingle folder (<TINGLE_FOLDER>) was left in place; delete it manually if you no longer need it.`
  - uninstall, nothing to remove (no `~/.bashrc` or no marker): `tingle is not installed in <BASHRC>`
  - All of these exit 0.
- **Shell scope:** bash only (`~/.bashrc`). No zsh or fish support. On macOS,
  bash login shells read `~/.bash_profile`, which must source `~/.bashrc`
  for the wiring to apply.
