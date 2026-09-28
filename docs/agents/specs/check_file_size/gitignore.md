# Spec: `.gitignore` support and `--no-gitignore`

Sub-issue: #251. Shared contracts: [README.md](README.md) (flags, precedence,
filter order, exit codes).

## Behaviour

- **On by default.** When `<path>` is inside a git work tree, files that git
  considers ignored are skipped.
- It follows git's own rules: nested `.gitignore` files, `.git/info/exclude`
  and the global excludes file (`core.excludesFile`).
- **Tracked files are always analysed**, even if they match a `.gitignore`
  pattern. Only untracked, ignored files are skipped.
- `--no-gitignore` (or config `"gitignore": false`) turns this step off.
- It runs after the path-component excludes and before `--ignore` (README
  section 5).
- If git is not installed, `<path>` is not in a work tree, or the git call
  fails for any reason, this step is **skipped silently**: no output and no
  change to the exit code.

## Examples

| Situation | Effect |
|-----------|--------|
| `.gitignore` has `*.log`, and `debug.log` is untracked | `debug.log` is skipped. |
| `.gitignore` has `*.log`, and `keep.log` is tracked (force-added) | `keep.log` is analysed. |
| `tingle check_file_size . --no-gitignore` | `.gitignore` is not consulted. |
| `tingle check_file_size /tmp/not-a-repo` | Nothing is skipped by git, and no warning is shown. |
| git not on `PATH` | Same as the line above. |

## Edge cases

- `<path>` is a subdirectory of the repository: only files under `<path>` are
  listed, and rules from parent `.gitignore` files still apply.
- `<path>` is a single file: the check runs from its parent directory, and the
  file is skipped if it is in the ignored set.
- An ignored directory (e.g. `node_modules/`) is reported by git as one entry.
  Every file under it is skipped.
- Nested repositories and submodules: only the repository that contains
  `<path>` is consulted.
- `.git/` itself is never in git's output. It stays covered by the default
  excludes (see [exclude.md](exclude.md)).

## Technical decisions

- New module `python/check_file_size/git_ignore.py`, exposing
  `GitIgnore.ignored_paths(root: Path) -> GitIgnored | None`:
  - It makes **one** call through `subprocess.run` with an argument list (no
    shell), `capture_output=True`, and no `check`:

    ```
    git -C <root> ls-files --others --ignored --exclude-standard --directory -z
    ```

    `root` is `<path>` for a directory, and its parent for a single file.
  - `ls-files` prints paths relative to `root` (without `--full-name`), so
    each entry is joined with `root` to make an absolute path.
    `rev-parse --show-toplevel` is not needed.
  - The output is split on `\0`, and empty entries are dropped. Entries ending
    in `/` (from `--directory`) are directory prefixes. Other entries are
    files.
  - It returns `None` on `FileNotFoundError` / `OSError` (git missing) or a
    non-zero exit code (for example 128, not a work tree). The collector
    treats `None` as "nothing ignored".
- `GitIgnored` (the same module) holds a `set[Path]` of files and a list of
  directory prefixes. `contains(path: Path) -> bool` is `True` when `path` is
  in the set or under a prefix.
- `FileCollector` gains `gitignore: bool` (default `True`). It calls
  `GitIgnore.ignored_paths` once per `collect()`, not once per file.
- `--no-gitignore` is `action: "store_true"` in `FLAGS`. `executor.py` resolves
  `gitignore = not no_gitignore`, merged with the config (README section 4).

## Tests expected

- `python/tests/check_file_size/test_git_ignore.py` (new):
  - parsing of NUL-separated output with file and directory (`/`) entries,
    and `contains()` for both;
  - `None` when `subprocess.run` raises `FileNotFoundError`, and when it
    returns a non-zero code (mocked);
  - an integration test in a temporary `git init` repository (skipped when
    git is unavailable): an ignored untracked file is listed, a tracked file
    that matches `.gitignore` is not, and nested `.gitignore` files are
    respected.
- `test_file_collector.py`: ignored files are dropped when enabled and kept
  with `gitignore=False`; `None` from the helper drops nothing.
- `test_executor.py`: `--no-gitignore` reaches the collector as
  `gitignore=False`.
