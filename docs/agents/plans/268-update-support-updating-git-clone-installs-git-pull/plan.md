# Plan: update: support updating git-clone installs (git pull)

Issue: [268-update-support-updating-git-clone-installs-git-pull.md](../../issues/268-update-support-updating-git-clone-installs-git-pull.md)

## Overview
Teach `tingle update` to update a git checkout of tingle. Today it refuses with a "use git pull" hint. It will validate the checkout, run `git pull --ff-only`, then `exec` the freshly pulled `bin/tingle install`. `--check` becomes a fetch plus a behind/ahead report, while a version pin and `--force` are refused. The web-install flow is unchanged. The shell agent implements the behavior, the cli agent updates the `--help` text in `commands/shell.json`, and the guide agent updates `docs/guides/update.md`.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

These user-visible messages are defined by the shell agent. The cli and guide agents describe them in their text, and must match the exact wording and exit codes. All of these messages go to stderr with the `tingle update: ` prefix unless marked stdout. `<folder>` is the tingle folder, `<branch>` is the current branch and `<upstream>` is its upstream (for example `origin/main`).

| Situation (git checkout) | Output | Exit |
|---|---|---|
| Start of run (both install kinds, unchanged) | stdout `Updating tingle in <folder>` | – |
| Pin given (`<version>` arg or `TINGLE_VERSION`) | `<folder> is a git checkout; version pins are not supported there. Check out a tag yourself instead, e.g. 'git -C <folder> checkout <version>'` | 1 |
| `--force` given | `--force is not supported on a git checkout (<folder>)` | 1 |
| `git` not on PATH | `required tool 'git' not found on PATH` | 1 |
| Tracked changes (staged or unstaged) | `<folder> has uncommitted changes; commit or stash them, then re-run; nothing was changed` | 1 |
| Detached HEAD | `<folder> is on a detached HEAD; check out a branch, then re-run; nothing was changed` | 1 |
| No upstream | `branch '<branch>' in <folder> has no upstream; set one with 'git branch --set-upstream-to', then re-run; nothing was changed` | 1 |
| `git fetch` fails | git's own error, then `could not fetch <upstream> in <folder>; nothing was changed` | 1 |
| Already up to date (behind = 0) | stdout `tingle is already up to date (<branch>, <short sha>)` | 0 |
| `--check` | stdout `<branch>: <N> commit(s) behind, <M> ahead of <upstream>` (the up-to-date line is printed instead when behind = 0) | 0 |
| `git pull --ff-only` fails (diverged, etc.) | git's own error, then `git pull --ff-only failed in <folder> (has the branch diverged from <upstream>?); nothing was changed` | 1 |
| Success | git's own pull output, then the output of `tingle install` (its exit status is the command's exit status) | install's |

- There is no confirmation prompt on the git path, and `TINGLE_ASSUME_YES` is ignored there.
- Untracked files do not count as "dirty".
- `curl`, `unzip` and `jq` are no longer required for the git path; only `git` is.
