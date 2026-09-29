# Add the git_ignore helper
Create `python/check_file_size/git_ignore.py` following
`docs/agents/specs/check_file_size/gitignore.md` ("Technical decisions"):

- `GitIgnored`: holds `files: set[Path]` and `dirs: list[Path]` (absolute
  paths). `contains(path: Path) -> bool` is `True` when `path` is in `files`
  or is under one of `dirs` (`path.is_relative_to(d)`).
- `GitIgnore.ignored_paths(root: Path) -> GitIgnored | None` (staticmethod,
  matching the class-with-static-methods style of `SkipChecks` /
  `GlobMatcher`):
  - one `subprocess.run(["git", "-C", str(root), "ls-files", "--others",
    "--ignored", "--exclude-standard", "--directory", "-z"],
    capture_output=True)` — argument list, no shell, no `check`;
  - return `None` on `OSError` (covers `FileNotFoundError`) or a non-zero
    `returncode`;
  - decode stdout, split on `"\0"`, drop empty entries; an entry ending in
    `/` goes to `dirs` as `root / entry.rstrip("/")`, others go to `files` as
    `root / entry`.

Add `python/tests/check_file_size/test_git_ignore.py`:
- parsing of mocked NUL-separated output with file and directory entries,
  and `contains()` for a file, a path under a directory prefix, and a
  non-ignored path;
- `None` when `subprocess.run` raises `FileNotFoundError` and when it
  returns a non-zero code (mocked with `monkeypatch`);
- the command is called once with the exact argument list above;
- integration in a temporary `git init` repo (skipped without git; global
  config isolated): an ignored untracked file is listed, a tracked
  (`git add -f`) file matching `.gitignore` is not, a nested `.gitignore`
  is respected, an ignored directory is reported as a prefix, and a
  non-repository directory returns `None`.

## Files to Change
- `python/check_file_size/git_ignore.py` — new `GitIgnore` / `GitIgnored`.
- `python/tests/check_file_size/test_git_ignore.py` — new unit and integration tests.
