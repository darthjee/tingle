# Issue: code_check js_complexity: skip minified bundles (*.min.js) by default

## Description
Skip minified bundles by default in `tingle code_check js_complexity` (parent #315), because they would always score CRITICAL and drown out real problems.

Spec: `docs/agents/specs/code_check/js_complexity/file-selection.md`, sections 1, 2, 4, 5 and 9.

## Problem
Repos often commit `*.min.js` files (vendored libraries, built assets) outside the default-excluded build folders. Their FTA scores are huge and say nothing about maintainability.

## Expected Behavior
- Files whose name ends in `.min.js`, `.min.mjs` or `.min.cjs` are skipped by default, case-insensitively (`app.MIN.JS` too). They are dropped silently and counted nowhere, like a default exclude.
- Only `--no-default-excludes`, or `"no_default_excludes": true` in the config, turns the skip off, together with the directory excludes. There is no separate switch.
- `--include` never brings minified files back: it only narrows the selection, so `--include '**/*.min.js'` alone selects nothing.
- A single-file `<path>` that is minified is skipped too (nothing to analyse, exit 0) unless `--no-default-excludes` is given. This differs from the directory excludes, which never apply to a single file.
- `.min.ts` and other names are not minified bundles. A minified file without `.min` in its name is analysed normally; the guide suggests `--ignore` for those.
- Declaration files stay skipped always, with or without `--no-default-excludes`.
- The `--no-default-excludes` help becomes `Do not skip the default directories or minified bundles; only --exclude names apply`, in `flags.py` and in the `js_complexity` part of `long_help` in `commands/python.json`.
- The guide `docs/guides/code_check/js_complexity.md` documents the skip, the single-file rule and the `--include` rule.

## Solution
- Add `MINIFIED_SUFFIXES = (".min.js", ".min.mjs", ".min.cjs")` to `python/code_check/js_complexity/constants.py`.
- Add an `is_minified(path)` predicate next to `is_declaration` in `python/code_check/js_complexity/selection.py`, checked on `path.name.lower()`.
- Give `js_complexity.selection.select_files` a way to know whether `no_default_excludes` resolved to true, and pass a combined `skip` predicate to `docker_check.selection.select_files`: declaration files always, then minified bundles unless `no_default_excludes` (filter order step 6).
- The executor passes the resolved `no_default_excludes` (flag or config) into the selection.
- No change to `docker_check`, `file_size` or `rubycritic`; their selection tests must still pass unchanged.

Depends on #321 (file selection flags), already merged.

### Tests
Under `python/tests/code_check/js_complexity/`:
- `.min.js`, `.min.mjs`, `.min.cjs` in any case skipped by default;
- kept with `--no-default-excludes` and with `"no_default_excludes": true`;
- still skipped with a matching `--include`;
- a minified single-file `<path>` skipped (exit 0) unless `--no-default-excludes`;
- `.min.ts` kept.

### Agents
- `python`: constants, predicate, selection/executor wiring, `flags.py` help and tests.
- `cli`: the `long_help` text in `commands/python.json`.
- `guide`: the guide update.

## Benefits
- Reports focus on hand-written code without manual `--ignore` setup.
