# Verify against scratch git repositories
In a `mktemp -d` scratch area, create a bare "upstream" repository from the current branch and clone it as the "install". Point `HOME` at a scratch directory so that `tingle install` writes a throwaway `~/.bashrc`. Run `<clone>/bin/tingle update` and check the output and exit code for each case:

- Up to date: the up-to-date line, exit 0, and `~/.bashrc` untouched.
- Behind by one commit (push a commit to the bare repo from a second clone): the pull succeeds, the install output follows, and HEAD equals the upstream.
- `--check` when behind: the `1 commit(s) behind, 0 ahead` line, exit 0, and HEAD unchanged.
- A modified tracked file: refused, exit 1.
- An untracked file: not refused.
- Detached HEAD (`git checkout --detach`): refused.
- No upstream (`git branch --unset-upstream`): refused.
- Diverged (a local commit plus a new upstream commit): the pull fails with git's error and the pull message, exit 1, and HEAD unchanged.
- `tingle update 0.5.0`, `TINGLE_VERSION=0.5.0 tingle update`, and `tingle update --force`: all refused before any git call.
- The web path, run against a web-install fixture or a `tingle.json` folder with the test-only `TINGLE_RELEASE_*` hooks: still behaves as before.

Also run `shellcheck shell/update/executor.sh`.

## Files to Change
- None (verification only).
