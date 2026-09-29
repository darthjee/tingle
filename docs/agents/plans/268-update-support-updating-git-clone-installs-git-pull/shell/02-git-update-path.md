# Implement the git update path
Add `git_update` to `shell/update/executor.sh`. Always run git as `git -C "$TINGLE_FOLDER"` and never `cd`. Checks run in this order, and each failure prints the exact message from the shared-contracts table and exits 1:

1. `PIN` is non-empty: refuse (no format validation first).
2. `--force` was given: refuse.
3. `git` is on PATH.
4. Dirty tree: `git diff --quiet` and `git diff --cached --quiet` (tracked files only; untracked files are ignored).
5. Detached HEAD: `git symbolic-ref -q --short HEAD` fails.
6. No upstream: `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'` fails.
7. `git fetch` (from the upstream's remote, which is the default when an upstream is set). On failure, let git's stderr through, then print the fetch message.
8. Compute `behind=$(git rev-list --count HEAD..@{u})` and `ahead=$(git rev-list --count @{u}..HEAD)`.
9. When `behind` is 0, print `tingle is already up to date (<branch>, <short sha>)` and exit 0. This applies both to `--check` and to a real run, and a real run does not re-run install in this case.
10. With `--check`, print `<branch>: <behind> commit(s) behind, <ahead> ahead of <upstream>` and exit 0.
11. Run `git pull --ff-only`. On failure, let git's output through, print the pull message and exit 1. The working tree is untouched, because ff-only never merges.
12. As the last statement: `exec "$TINGLE_FOLDER/bin/tingle" install`, so that the freshly pulled entry point and installer run.

There is no confirmation prompt and no `TINGLE_ASSUME_YES` handling here.

## Files to Change
- `shell/update/executor.sh` — add `git_update` implementing the above.
