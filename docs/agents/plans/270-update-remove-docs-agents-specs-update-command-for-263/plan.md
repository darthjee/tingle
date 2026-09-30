# Plan: update: remove docs/agents/specs/update_command/ for #263

Issue: [270-update-remove-docs-agents-specs-update-command-for-263.md](../../issues/270-update-remove-docs-agents-specs-update-command-for-263.md)

## Overview
This is the last sub-issue of #263. It changes no behaviour. First, each
permanent home of the `tingle update` contracts fills the gaps found when it
was compared with the specs: the user guide, `tingle-release-zip.md`, the
installer and executor header comments, and the `update` `long_help`. Then
the product-owner deletes `docs/agents/specs/update_command/` and its row in `docs/agents/specs.md`.
The PR closes #270 and #263.

## Agents involved

- [guide](guide.md): runs first
- [shell](shell.md)
- [cli](cli.md)
- [architect](architect.md)
- [product-owner](product-owner.md): runs last, and deletes the specs only
  after every other agent's gaps are filled

## Shared contracts

- **Code is the truth.** Where the specs and the code disagree, document the
  code. Where the code is `shell/update/executor.sh`, `install/update.sh`,
  `install/manifest.sh`, `install/installer.sh` or `scripts/release_cli.sh`,
  that code wins.
- **#268 supersedes the git-checkout refusal.** A git checkout is
  fast-forwarded with `git pull --ff-only`, then `tingle install` is
  re-run. No doc may reintroduce the specs' "use `git pull`" refusal.
- **`version: "unknown"`** (the `TINGLE_VERSION` default when installing
  from a checkout) is always treated as out of date. `--check` shows
  `unknown → <latest>`. Such an install does not track hashes.
- **Empty manifest.** `"manifest": []` means the install does not track
  hashes. On update, nothing is deleted, and a warning says stale files may
  be left behind.
- **Exit codes.** Exit 0 means an update completed, a `--check`, or
  "already up to date". Every refusal or failure exits non-zero. After the
  executor hands off (`exec`), the exit status is the installer's own.
- The spec files are deleted in this PR, so no doc may link to
  `docs/agents/specs/update_command/`.
