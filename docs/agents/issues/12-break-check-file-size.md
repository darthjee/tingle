# Issue: Set up ruff lint for python/

## Description
`python/check_file_size/` was already broken down into its package structure (classes, `Reporter`, generic `ArgParser` in `python/common/`, hub routing, docs) as part of issue #10/PR #11. What remains from this issue's original scope is lint tooling for `python/`, which was never picked up. Unit test setup (pytest, docker, CI) is tracked separately.

## Problem
There is no lint tooling configured for `python/` yet (tracked as an open item in `docs/agents/todo.md`), so regressions in style/correctness in `python/check_file_size/` and `python/common/` are only caught by manual review.

## Expected Behavior
`ruff check python/` runs clean and is documented as the lint command for the `python` agent.

## Solution
- Add a `ruff` configuration for `python/`.
- Fix any violations `ruff check python/` reports against the existing `check_file_size` package and `common/arg_parser.py`.
- Update `docs/agents/todo.md` / the `python` agent doc to record `ruff check python/` as the configured lint command.
- No changes to CLI flags, output format, or `bin/tingle` routing.

## Benefits
- Style/correctness regressions in `python/` are caught automatically instead of relying on manual review.
- Closes the outstanding lint-tooling item tracked in `docs/agents/todo.md` for the `python` agent.
