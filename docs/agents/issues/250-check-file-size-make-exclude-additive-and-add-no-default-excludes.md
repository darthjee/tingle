# Issue: check_file_size: make --exclude additive and add --no-default-excludes

## Description
Part of #247. `tingle check_file_size` is implemented in `python/check_file_size/` (`executor.py` holds the `FLAGS` and builds the `FileCollector`, `file_collector.py` walks and filters files, `constants.py` holds `DEFAULT_EXCLUDES`). The normative spec for this sub-issue is [`docs/agents/specs/check_file_size/exclude.md`](../specs/check_file_size/exclude.md); the shared contracts (flags, precedence, filter order, exit codes) are in [`docs/agents/specs/check_file_size/README.md`](../specs/check_file_size/README.md). Read both before starting. Merge order: after #249, before #251.

## Problem
- `--exclude` **replaces** `Constants.DEFAULT_EXCLUDES`. To skip one extra directory you have to repeat the whole default list.
- `FileCollector._is_excluded` checks every component of the **absolute** path (`path.parts`), so directories above `<path>` count too. Running inside e.g. `~/work/build/my-app` excludes every file (`No files found for analysis.`).

## Expected Behavior
- `--exclude a,b` **adds** `a` and `b` to the default excluded names.
- New flag `--no-default-excludes` (`store_true`, parsed as `no_default_excludes`) drops `DEFAULT_EXCLUDES`. Only the `--exclude` names (if any) apply.
- A file is excluded when any component of its path **relative to `<path>`** equals an exclude name, case-insensitively and as a whole component (`build` excludes `build/x.js` and `a/build/y.js`, not `builder/z.js`). Components of `<path>` and its parents are no longer checked.
- Path-component excludes still do not apply when `<path>` is a single file.
- Entries are comma-separated, blanks are trimmed, empty entries dropped (`--exclude ' fixtures, ,tmp'` gives `fixtures`, `tmp`). `--exclude ''` / `--exclude ,` adds nothing.
- Names already in the defaults (`--exclude dist`) are deduplicated with no error.
- Names are not globs (`--exclude '*.tmp'` matches a component literally named `*.tmp`; use `--ignore` for globs).
- `--exclude` stays non-repeatable (last one wins).
- **Breaking change**: `--exclude fixtures` now skips `fixtures` *and* the defaults. The old meaning is `--no-default-excludes --exclude fixtures`.

| Invocation | Excluded names |
|------------|----------------|
| `tingle check_file_size .` | The defaults |
| `tingle check_file_size . --exclude fixtures` | The defaults + `fixtures` |
| `tingle check_file_size . --no-default-excludes` | None (`.git/` is walked too) |
| `tingle check_file_size . --no-default-excludes --exclude fixtures` | Only `fixtures` |

## Solution
- `python` agent, `executor.py`:
  - `--exclude` gets `default: None`; its help lists the defaults and says the names are **added** to them.
  - Add `--no-default-excludes` to `FLAGS`.
  - Build the final list: (`DEFAULT_EXCLUDES` unless `no_default_excludes`) + the split `--exclude` names, deduplicated in order, and pass it to `FileCollector` (which keeps receiving one resolved `excludes` list and does not know about the defaults).
  - Update the examples in the module docstring.
- `python` agent, `file_collector.py`: `_is_excluded` checks the parts of the path relative to `<path>` (reusing the relative path computed for #249), not `path.parts`.
- `python` agent, tests under `python/tests/check_file_size/`:
  - `test_executor.py`: no flag gives defaults; `--exclude x` gives defaults + `x`; `--no-default-excludes` gives empty; both give only `x`; blank entries dropped; duplicates removed.
  - `test_file_collector.py`: a component of `<path>` itself equal to an exclude name does not exclude files below it; whole-component, case-insensitive match; not applied to a single-file `<path>`.
- `python` agent (or `cli`): update the `check_file_size` `long_help` in `commands/python.json` to document `--exclude` ("adds to the defaults") and `--no-default-excludes`.
- `guide` agent, `docs/guides/check_file_size.md`: update the options table, rewrite the `--exclude` section (drop the "replaces the default list" warning, the "repeat the default list" workaround and the "whole absolute path" caveat), add `--no-default-excludes` with examples, and add the migration note from the spec:
  > `--exclude` now **adds** to the default excludes instead of replacing them. `--exclude fixtures` now also skips `node_modules`, `dist`, `build`, etc. For the old behaviour, use `--no-default-excludes --exclude fixtures`.
- Out of scope: the config file `exclude` / `no_default_excludes` keys (#253).

## Benefits
- Adding one excluded directory no longer means repeating the defaults.
- Projects living under a directory named like a default exclude (`build`, `out`, `target`, ...) can be analysed.
