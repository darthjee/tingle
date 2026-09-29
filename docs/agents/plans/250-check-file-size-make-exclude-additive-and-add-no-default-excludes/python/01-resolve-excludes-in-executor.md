# Resolve the exclude list in the executor

Make `--exclude` additive and add `--no-default-excludes`.

- In `FLAGS`, change `--exclude` to `default: None`. Its help becomes something like
  `"Extra directory names to skip (comma-separated), added to the defaults: <defaults>"`.
- Add a `--no-default-excludes` entry (`action: "store_true"`, help: "Do not skip the
  default directories; only --exclude names apply"). Check that `common/arg_parser.py`
  passes `action` through without a `type` (as `--ext`/`--ignore` do with `append`). If
  `store_true` with no `type` is not supported, add the minimal support there.
- Add a helper `CheckFileSize._resolve_excludes(args: dict) -> list[str]`:
  base = `[]` if `args["no_default_excludes"]` else `list(Constants.DEFAULT_EXCLUDES)`,
  extra = `_parse_excludes(args["exclude"] or "")`, then return
  `list(dict.fromkeys(base + extra))`.
- In `run`, pass `self._resolve_excludes(args)` to `FileCollector` instead of
  `self._parse_excludes(args["exclude"])`.
- Update the module docstring examples: `--exclude fixtures` (adds to the defaults) and
  `--no-default-excludes --exclude fixtures`.

## Files to Change
- `python/check_file_size/executor.py` — `FLAGS`, `_resolve_excludes`, `run`, docstring examples.
- `python/common/arg_parser.py` — only if `store_true` flags are not supported yet.
