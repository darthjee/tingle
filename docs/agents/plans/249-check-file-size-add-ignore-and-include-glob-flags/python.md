# Python Plan: check_file_size: add --ignore and --include glob flags

Main plan: [plan.md](plan.md)

## Shared contracts

- Flags `--ignore GLOB` / `--include GLOB` in `FLAGS`: `type: str`,
  `action: "append"`, `default: None` (treat `None` as `[]`). Use the help
  texts from [plan.md](plan.md).
- Matching rules, anchoring, precedence and filter order: exactly as in
  [plan.md](plan.md) and
  [ignore-include.md](../../specs/check_file_size/ignore-include.md).

## Steps

- [01 — Add GlobMatcher](python/01-add-glob-matcher.md)
- [02 — Apply globs in FileCollector](python/02-apply-globs-in-file-collector.md)
- [03 — Wire the flags into executor.py](python/03-wire-flags-into-executor.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)

## Notes
- Python 3.11 has no `PurePath.full_match`, and `fnmatch` lets `*` cross `/`.
  So do not use `fnmatch.translate`: write a small tokenizer.
- #250 and #251 also change `FileCollector` and merge after this issue. Keep
  the new constructor arguments keyword-friendly and the per-file filter easy
  to extend. The current positional `(excludes, extensions)` signature must
  keep working for existing callers and tests.
