# Issue: code_check rubycritic: add --exclude/--ignore/--include and .gitignore file selection

## Description
Add the file selection flags to `tingle code_check rubycritic` (parent #290). They mean the same as in `tingle code_check file_size`, and `file_size`'s `FileCollector` is reused directly, not copied. The full contract is in `docs/agents/specs/code_check/rubycritic/file-selection.md`. That spec is the source of truth for this issue.

Depends on #295 (subcommand core), which is already merged.

## Problem
Today `select_files` in `python/code_check/rubycritic/selection.py` builds a `FileCollector` with only the default excludes and the `.rb` filter. It passes `gitignore=False` and `binary_check=False`, and no globs. So users cannot narrow or widen what is analysed. Git-ignored Ruby files are analysed. A symlink pointing outside `<path>` is sent to the container, which cannot see it through its read-only mount.

## Expected Behavior
- `--exclude a,b` adds comma-separated directory names to the default excludes. Blank entries are dropped and duplicates are removed. As in `file_size`, the flag is not repeatable: a second `--exclude` replaces the first.
- `--no-default-excludes` drops the 16 default excludes (`Constants.DEFAULT_EXCLUDES`), so only `--exclude` names apply.
- `--ignore GLOB` (repeatable) skips files whose path relative to `<path>` matches the glob.
- `--include GLOB` (repeatable) keeps only files that match at least one include glob. A file must match an include glob **and** end in `.rb`. There is no `--ext`.
- `.gitignore` is respected by default when `<path>` (or a single file's parent) is inside a git work tree. Tracked files are always kept. When git is missing or fails, nothing is skipped and nothing is printed. `--no-gitignore` turns the check off.
- Filter order: (1) default excludes, (2) `--exclude`, (3) `.gitignore`, (4) `--ignore`, (5) `--include` + `.rb`, (6) symlink confinement. The first step that rejects a file drops it.
- Symlink confinement: a file is skipped silently when its resolved path is outside the resolved mount root. This covers outside targets and dangling links. A kept symlink is analysed as its target: the target's relative path goes on stdin and in the report. The selection is deduplicated by resolved path. Directory symlinks are still not walked into.
- For a single-file `<path>`, path-component excludes do not apply, and globs match the file name.
- The binary check stays off (`binary_check=False`), so non-UTF-8 `.rb` files still reach the image and show as `PARSE` rows.
- `file_size`'s behaviour does not change.

## Solution
- `FileCollector` (`python/code_check/file_size/file_collector.py`) gains a keyword-only `outside_symlinks: bool = True`. When it is `False`, step 6 applies. The default keeps `file_size` unchanged.
- The rubycritic executor and `selection.py` build `FileCollector(excludes, [".rb"], ignore=..., include=..., gitignore=..., binary_check=False, outside_symlinks=False)`. They resolve the excludes the way `file_size`'s `_resolve_excludes` does, sharing that helper where sensible.
- Add `--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore` and `--include` to `python/code_check/rubycritic/flags.py`, with the help texts from the spec. Completion picks them up from there. `--exclude`, `--ignore` and `--include` take free-form values.
- Add a "File selection" block to the rubycritic part of `long_help` in `commands/python.json`, with examples.
- Update the guide page `docs/guides/code_check/rubycritic.md`.
- Add tests under `python/tests/code_check/rubycritic/` for:
  - each flag
  - the filter order (a file matched by several steps is dropped by the first)
  - a single-file `<path>`
  - symlinks: inside, outside, absolute-inside and dangling
  - a non-UTF-8 `.rb` file being kept
- `file_size`'s collector tests must still pass unchanged.

Out of scope: the `rubycritic` config section and `--no-config` (#297), and removing the specs (#298).

## Agents
- `python`: `FileCollector`, rubycritic selection/executor/flags/completion, tests.
- `cli`: the `long_help` in `commands/python.json`.
- `guide`: `docs/guides/code_check/rubycritic.md`.

## Benefits
- Ruby users get the same file selection controls as in `file_size`.
- Git-ignored or vendored Ruby code no longer skews the complexity report.
- Files the container cannot see are never sent to it.
