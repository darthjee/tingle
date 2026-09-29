# Shell Plan: update: support updating git-clone installs (git pull)

Main plan: [plan.md](plan.md)

## Shared contracts

The shell agent produces every message and exit code in the table in [plan.md](plan.md#shared-contracts), word for word. It must also keep the web-install flow's existing messages and behavior exactly as they are.

## Steps

- [01 — Restructure detection so the git path runs first](shell/01-restructure-detection.md)
- [02 — Implement the git update path](shell/02-git-update-path.md)
- [03 — Update the executor header comment](shell/03-header-comment.md)
- [04 — Verify against scratch git repositories](shell/04-verify.md)

## CI Checks
- CI (`.circleci/config.yml`) only runs Python lint and tests, plus release jobs; there is no shell job. Run `shellcheck shell/update/executor.sh` locally.

## Notes
- The repo has no shell test harness, so verification is a scripted manual run against throwaway git repositories (step 04), not a committed test suite. If the implementer thinks a small committed test script is worth adding, it should be raised as a follow-up issue rather than done in this one.
- Self-overwrite: `git pull` may replace `shell/update/executor.sh` while it is running. Git writes new files and renames them into place, so bash keeps reading the old inode. Still, nothing substantial should run between the pull and the `exec` of the new `bin/tingle install`.
