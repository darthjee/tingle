# Plan: Set up ruff lint for python/

Issue: [12-break-check-file-size.md](../issues/12-break-check-file-size.md)

## Overview
Add a `ruff` configuration scoped to `python/`, fix whatever violations it reports against the existing `check_file_size` package and `common/arg_parser.py`, and document `ruff check python/` as the configured lint command — closing the outstanding item in `docs/agents/todo.md`. No behavior, CLI flag, or routing changes.

## Agents involved

- [python](python.md)
- [product-owner](product-owner.md)

## Shared contracts

- Lint command: `ruff check python/`, run from the repo root. `product-owner` documents this exact command string in `docs/agents/todo.md`; `python` is responsible for making it pass (config file + any fixes).
- Config location: the `python` agent owns the ruff config file (e.g. `python/pyproject.toml` or `python/ruff.toml`) — kept inside `python/` rather than at repo root, matching ruff's config auto-discovery when a `python/` target path is scanned.
