# Plan: install: add update mode to installer.sh

Issue: [265-install-add-update-mode-to-installer-sh.md](../../issues/265-install-add-update-mode-to-installer-sh.md)

## Overview
Add an update mode to `install/installer.sh`, switched on by
`TINGLE_UPDATE_TARGET`, that updates an existing web install in place:
preflight (lock, validity, edited-file check), stage next to targets, swap
by rename, prune, commit `tingle.json` last, then wire via a child
`bin/tingle install`. The architect implements the installer (`install/`
has no specialist). The product-owner syncs the `update_command` specs with
the decisions made while refining the issue.

## Agents involved

- [architect](architect.md)
- [product-owner](product-owner.md)

## Shared contracts

Update-mode environment variables (owned by #265, consumed by #266):

| Variable | Type / values | Meaning |
|----------|---------------|---------|
| `TINGLE_UPDATE_TARGET` | path; `~` expanded, relative made absolute | Install folder to update. Presence switches on update mode. |
| `TINGLE_UPDATE_FORCE` | `1` or unset | Overwrite locally edited shipped files. |
| `TINGLE_UPDATE_CLEANUP` | `1` or unset | Remove the source tree (the dir the installer runs from) on exit. `tingle update` sets it; unset when run by hand. |
| `TINGLE_REPO` | `owner/repo` | Repo recorded in the new `tingle.json` (as today). |
| `TINGLE_VERSION` | tag | Version recorded in the new `tingle.json` (as today). |

Additional behaviour the specs must record:
- Lock: `<target>/.tingle-update.lock/` directory with a `pid` file.
- Staged files: `<dir>/.<name>.tingle-new`, same permissions as the source file.
- `MANIFEST` itself is staged and swapped too, so `<target>/MANIFEST`
  matches the new `tingle.json`.
- A missing, malformed or empty incoming `MANIFEST` is refused in preflight
  with no change.
- Absolute or `..` manifest paths are skipped with a warning for every
  path hashed, staged, swapped or pruned.
