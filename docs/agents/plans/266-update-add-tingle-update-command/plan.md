# Plan: update: add tingle update command

Issue: [266-update-add-tingle-update-command.md](../../issues/266-update-add-tingle-update-command.md)

## Overview
Add `tingle update [--check] [--force] [<version>]`, a thin shell command
under `shell/update/`. It detects the web install that the running
`bin/tingle` belongs to, resolves and validates a target version, downloads
and verifies the release zip into a temp dir, then `exec`s the new release's
`install/installer.sh` in update mode (merged in #265). The shell agent writes
the command, and the cli agent registers it in `commands/shell.json`.

The full behaviour is fixed in the spec
[update-command.md](../../specs/update_command/update-command.md) and its
shared contracts [README.md](../../specs/update_command/README.md). They win
over this plan if they disagree.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)

## Shared contracts

- **Command registration:** `commands/shell.json` key `"update"`, with
  `"path": "shell/update/main.sh"`. `bin/tingle` runs
  `shell/update/main.sh run <args...>`, and `main.sh` `exec`s
  `executor.sh "$@"`, like `shell/uninstall/`.
- **CLI surface (documented in `long_help`, implemented by the executor):**
  - `tingle update [--check] [--force] [<version>]`
  - `<version>` / `TINGLE_VERSION`: pin, `X.Y.Z` or `X.Y.Z-<suffix>`, no
    `v` prefix, 0.4.0 or later; the argument wins over the env var; downgrade
    and pre-release pins allowed.
  - `--check`: print installed → target (and locally edited shipped files
    when hashes are tracked), exit 0, change nothing.
  - `--force`: overwrite locally edited shipped files.
  - `TINGLE_ASSUME_YES`: skip the y/N prompt.
  - A git checkout (no `tingle.json`, `.git` at the root) is told to use
    `git pull` and exits non-zero.
- **Fixed messages** (printed exactly):
  - `tingle is already up to date (<version>)`
  - `release <version> not found in <repo>`
  - `tingle update can only install 0.4.0 or later`
- **Test-only hooks:** `TINGLE_RELEASE_API_URL` and
  `TINGLE_RELEASE_BASE_URL` are documented only in the header of
  `shell/update/executor.sh`, **never** in `long_help`.
