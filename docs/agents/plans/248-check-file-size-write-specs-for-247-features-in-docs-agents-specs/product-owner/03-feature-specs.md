# Write one spec per feature
Create five files under `docs/agents/specs/check_file_size/`. Each has these sections: **Behaviour**, **Examples** (CLI invocations + expected effect), **Edge cases**, **Technical decisions**, **Tests expected**, and a link back to `README.md` and to its sub-issue.

- `ignore-include.md` (#249)
  - Globs are matched against the POSIX-style path **relative to `<path>`** (for a single-file `<path>`, its file name). Matching is **case-insensitive**, consistent with `--exclude`/`--ext`.
  - `*`, `?` and `[...]` never cross `/`. `**` as a whole segment matches zero or more directories (`**/x`, `a/**`, `a/**/b`). A pattern without `/` matches the file name in any directory, as in `.gitignore`.
  - Decision: add a small helper module (e.g. `python/check_file_size/glob_matcher.py`) that compiles each glob to a regex once (`re.IGNORECASE`), since Python 3.11 has no `PurePath.full_match`. It gets its own unit tests.
  - An empty `--include` list means include everything.
- `exclude.md` (#250)
  - `--exclude` now adds to `Constants.DEFAULT_EXCLUDES` (its argparse default becomes empty). `--no-default-excludes` drops the defaults.
  - Matching is still case-insensitive per path component, against the path relative to `<path>` if that is how the code works after #249. Otherwise, keep the current absolute-path behaviour and note it.
  - **Breaking change**: add a migration note for the guide (`--exclude fixtures` now also skips `node_modules`, etc., so use `--no-default-excludes --exclude fixtures` for the old behaviour).
- `gitignore.md` (#251)
  - On by default. Decision: one call, `git -C <root> ls-files --others --ignored --exclude-standard -z` (plus `--directory` if needed for speed), run via `subprocess` with no shell. Resolve paths against `git rev-parse --show-toplevel` and turn them into a set of absolute paths, or directory prefixes for `--directory` entries.
  - This respects nested `.gitignore` files, `.git/info/exclude` and the global excludes file. Tracked files are always analysed.
  - Fallback: git missing (`FileNotFoundError`), non-zero exit, or not a work tree → skip silently (no output, no exit-code change).
  - `--no-gitignore` / config `gitignore: false` disables it. Decision: helper module `python/check_file_size/git_ignore.py`.
- `min-level.md` (#252)
  - `--min-level ok|warn|error|critical` (default `ok`). Only rows at or above the level are shown (OK < WARN < ERROR < CRITICAL), reusing the level ordering from `--fail-on`.
  - Applied before `--top`. Summary counts and the gate are unaffected.
  - When no row passes: print the summary plus a one-line note (e.g. `No files at or above WARN.`), not an empty table header.
  - An invalid value is a usage error → exit 1.
- `config.md` (#253)
  - Path: `$HOME/.tingle/code_check/config.json` (`Path.home()`). Top level is a JSON object, and the `check_file_size` key holds the options.
  - Schema: key → type (`warn`/`error`/`critical`/`top`: int ≥ 0; `exclude`/`ignore`/`include`/`ext`: list of str; `no_default_excludes`/`gitignore`: bool; `fail_on`: `warn|error|critical|null`; `min_level`: `ok|warn|error|critical`). Merge rules come from `README.md`.
  - Errors → message on stderr (`Error: <config path>: <reason>`), exit 1: invalid JSON, top level not an object, unknown key, wrong type or value. A missing file or missing section is fine, and other top-level sections are ignored (reserved for the future `code_check` tool).
  - Decision: `python/check_file_size/config.py` exposes a generic `load_section(name)` so `code_check` can reuse it, and merging happens in `executor.py` after argparse. To tell "not passed" from "default", the argparse defaults become `None`, and the built-in defaults are applied after merging.
  - Tests use a temporary `HOME`.

## Files to Change
- `docs/agents/specs/check_file_size/ignore-include.md` — new.
- `docs/agents/specs/check_file_size/exclude.md` — new.
- `docs/agents/specs/check_file_size/gitignore.md` — new.
- `docs/agents/specs/check_file_size/min-level.md` — new.
- `docs/agents/specs/check_file_size/config.md` — new.
