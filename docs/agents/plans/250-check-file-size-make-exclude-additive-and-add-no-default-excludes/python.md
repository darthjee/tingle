# Python Plan: check_file_size: make --exclude additive and add --no-default-excludes

Main plan: [plan.md](plan.md)

## Shared contracts

- Produce `--exclude` (`type=str`, `default=None`, non-repeatable) and
  `--no-default-excludes` (`store_true`, key `no_default_excludes`) in `FLAGS`.
- Final list = (`Constants.DEFAULT_EXCLUDES` unless `no_default_excludes`) + split
  `--exclude` names, trimmed, empties dropped, deduplicated in order.
- `FileCollector` keeps receiving one resolved `excludes` list. It knows nothing about
  the defaults or the flags.
- Matching is whole-component, case-insensitive, relative to `<path>`, and never applied
  to a single-file `<path>`.
- The `--exclude` help text says the names are **added** to the defaults and lists them.

## Steps

- [01 — Resolve the exclude list in the executor](python/01-resolve-excludes-in-executor.md)
- [02 — Match excludes on the relative path](python/02-relative-path-excludes.md)
- [03 — Tests](python/03-tests.md)

## CI Checks
- `python/`: `ruff check .` (CI job: lint)
- `python/`: `pytest` (CI job: tests)

## Notes
- `CheckFileSize.run` is already flagged by Codacy for cyclomatic complexity (#202).
  Put the merging logic in a helper (e.g. `_resolve_excludes(args) -> list[str]`), not
  inline in `run`.
- Behaviour change: `--exclude x` used to mean "only `x`". Existing tests that pass
  `--exclude` and assume the defaults are gone must be updated, not deleted.
- Config file keys (`exclude`, `no_default_excludes`) belong to #253. Do not read any
  config here.
