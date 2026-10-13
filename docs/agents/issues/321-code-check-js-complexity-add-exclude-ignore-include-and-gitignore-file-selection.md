# Issue: code_check js_complexity: add --exclude/--ignore/--include and .gitignore file selection

## Description
Add the file-selection flags to `tingle code_check js_complexity` (parent #315), with the same meaning as in `file_size` and `rubycritic`, through the shared `docker_check` selection.

Spec: [`docs/agents/specs/code_check/js_complexity/file-selection.md`](../specs/code_check/js_complexity/file-selection.md) (sections 1, 3, 5, 6, 7 and 9).

## Problem
The subcommand added in #320 only applies the built-in extension list, the default excludes and the declaration-file skip, and it calls `js_complexity.selection.select_files` with `gitignore=False`. Users can't skip test folders or generated code, focus on `src/`, or rely on `.gitignore`.

## Expected Behavior
- `--exclude LIST`: comma-separated directory names, **added** to the 19 default excludes, blank entries dropped, deduplicated (`code_check.excludes.resolve_excludes`). Not repeatable: a second `--exclude` replaces the first.
- `--no-default-excludes`: drops the defaults, so only the `--exclude` names apply. Declaration files stay skipped.
- `--ignore GLOB` (repeatable): skips files whose path relative to `<path>` matches (`GlobMatcher` semantics).
- `--include GLOB` (repeatable): only keeps files that match at least one include glob **and** have a supported extension.
- `.gitignore` is respected by default (`.gitignore`, `.git/info/exclude`, global excludes), via one `git ls-files` call on the host; `--no-gitignore` turns that off. Without git, outside a work tree or when git fails, nothing is skipped and nothing is printed.
- Filter order is the spec's section 5 (default excludes → `--exclude` → gitignore → `--ignore` → `--include` + extensions → declaration skip → symlink confinement); the first step that rejects a file drops it.
- For a single-file `<path>`, the globs match the file name and the directory excludes don't apply; gitignore, globs, skip rules and confinement still do.
- Help texts are the spec's section 1 texts; the `--no-default-excludes` help ends at "directories" (the minified part is added by #323).
- `--help` (`long_help` in `commands/python.json`), completion (`--exclude`, `--ignore`, `--include` take free-form values) and the guide's "File selection" section in `docs/guides/code_check/js_complexity.md` are updated.
- Tests under `python/tests/code_check/js_complexity/` cover each flag, the filter order (a file matching several steps is dropped by the first), single-file `<path>`, symlinks (inside, outside, absolute-inside, dangling), upper-case extensions and declaration files in every suffix and case, with `docker` mocked. `file_size`'s and `rubycritic`'s selection tests pass unchanged.

## Solution
- `python/code_check/js_complexity/flags.py`: add the five flag definitions, mirroring `rubycritic/flags.py` with the JS/TS help texts.
- `python/code_check/js_complexity/executor.py`: resolve the excludes with `code_check.excludes` and pass `excludes`, `ignore`, `include` and `gitignore=not no_gitignore` to `js_complexity.selection.select_files`, which already accepts them (the `docker_check.selection` plumbing exists since #317/#320).
- No change to `docker_check`, `file_size` or `rubycritic`.

Depends on #320 (merged).

### Out of scope
- The config keys for these flags and `--no-config` (#322).
- The minified skip (#323).
- SFC extensions (#326).

### Agents
- `python`: flags, executor wiring and tests.
- `cli`: `long_help` and completion.
- `guide`: the guide's "File selection" section.

## Benefits
- The selection behaves the same in every `code_check` subcommand.
- Users can scope the analysis to the code they own, without vendored or generated files skewing the report.
