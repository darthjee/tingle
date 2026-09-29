# Issue: check_file_size: respect .gitignore by default, add --no-gitignore

## Description
Part of #247. `tingle check_file_size` is implemented in `python/check_file_size/` (`executor.py` holds the flags, `file_collector.py` walks and filters files, `constants.py` holds `DEFAULT_EXCLUDES`, `reporter.py` prints the table). The normative contract for this sub-issue is `docs/agents/specs/check_file_size/gitignore.md`, together with the shared contracts in `docs/agents/specs/check_file_size/README.md` (flags, precedence, filter order, exit codes). Read both before starting; if this issue and the specs disagree, the specs win.

#249 (`--ignore` / `--include`) and #250 (additive `--exclude`, `--no-default-excludes`) are already merged, so this change builds on the current `FileCollector`.

## Problem
Files ignored by git (build output, generated files, local data) are counted today unless one of their path components is in the default excludes or `--exclude`. Running the command on a real repository therefore reports files that are not part of the project.

## Expected Behavior
- **On by default**: when `<path>` is inside a git work tree, untracked files that git ignores are skipped. Git's own rules apply: nested `.gitignore` files, `.git/info/exclude` and the global excludes file (`core.excludesFile`).
- **Tracked files are always analysed**, even when they match an ignore pattern (as git does).
- `--no-gitignore` turns the step off.
- If `git` isn't installed, `<path>` isn't in a work tree, or the git call fails for any reason, the step is **skipped silently**: no output, no change to the exit code.
- Works for both a directory and a single-file `<path>` (for a single file, git runs from its parent directory and the file is skipped if it is ignored).
- A subdirectory `<path>` still honours parent `.gitignore` files. An ignored directory (e.g. `node_modules/`) skips every file under it. Only the repository containing `<path>` is consulted (no nested repos/submodules).
- Filter order in `FileCollector` (specs README section 5): default excludes → `--exclude` → **.gitignore** → `--ignore` → `--include`/`--ext` → binary check.

## Solution
- `python` agent:
  - New module `python/check_file_size/git_ignore.py` exposing `GitIgnore.ignored_paths(root: Path) -> GitIgnored | None`. It makes **one** `subprocess.run` call (argument list, no shell, `capture_output=True`, no `check`): `git -C <root> ls-files --others --ignored --exclude-standard --directory -z`. Output is split on `\0`, empty entries dropped, entries ending in `/` are directory prefixes, the rest are files; each is joined with `root`. Returns `None` on `FileNotFoundError`/`OSError` or a non-zero exit code.
  - `GitIgnored` holds a `set[Path]` of files and a list of directory prefixes; `contains(path)` is `True` when the path is in the set or under a prefix. Paths from git and from the walk must be compared in the same form (e.g. both resolved), so a relative `<path>` such as `.` works.
  - `FileCollector` gains `gitignore: bool = True` and calls the helper once per `collect()`, not per file; `None` means nothing is ignored.
  - `--no-gitignore` is `action: "store_true"` in `FLAGS`; `executor.py` passes `gitignore = not no_gitignore` to the collector. Update the flag help and the examples in the `executor.py` module docstring.
  - Update `long_help` of `check_file_size` in `commands/python.json`.
  - Tests: new `python/tests/check_file_size/test_git_ignore.py` (NUL-separated parsing with file and directory entries, `contains()`, `None` on `FileNotFoundError` and on non-zero exit (mocked), integration test in a temporary `git init` repo — skipped when git is unavailable — covering an ignored untracked file, a tracked file matching `.gitignore`, and nested `.gitignore`); `test_file_collector.py` (dropped when enabled, kept with `gitignore=False`, `None` drops nothing); `test_executor.py` (`--no-gitignore` reaches the collector as `gitignore=False`).
- `guide` agent: update `docs/guides/check_file_size.md` (options table plus a section with examples).
- Out of scope: the config key `gitignore` (handled by #253) and any `--verbose` / `--list-ignored` mode.

## Benefits
The results match what's actually tracked in the repository, without having to repeat `.gitignore` rules through `--exclude` or `--ignore`.
