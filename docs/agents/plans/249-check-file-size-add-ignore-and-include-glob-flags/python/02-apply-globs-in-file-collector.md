# Apply globs in FileCollector
Extend `FileCollector.__init__` with `ignore: list[str] | None = None` and
`include: list[str] | None = None`, and build one `GlobMatcher` for each
(`None` → `[]`). Keep the existing positional `(excludes, extensions)`
arguments.

In `collect`:
- **Directory target:** for each file that survives the exclude check,
  compute `rel = path.relative_to(target).as_posix()` once. Then drop the file
  if the ignore matcher matches `rel`. Then, when include patterns exist, drop
  the file unless the include matcher matches `rel`. Then apply the `--ext`
  check (AND with `--include`), and finally the binary check.
- **Single-file target:** use `rel = target.name`, apply the same ignore and
  include/ext checks, then the binary check. Path-component excludes still do
  not apply.

To stay under the complexity limit, move the per-file decision into a helper
such as `_accepts(path, rel) -> bool`. That also gives #250 and #251 one place
to hook into.

Tests to add in `python/tests/check_file_size/test_file_collector.py`:
- `--ignore` drops matches, including an anchored pattern such as `tests/fixtures/**`;
- `--include` keeps only matches;
- `--include` together with `--ext` is an AND;
- `--ignore` wins over `--include`;
- a single-file target matches on its name, for both ignore and include;
- the existing tests still pass unchanged.

## Files to Change
- `python/check_file_size/file_collector.py` — new `ignore`/`include` arguments and filtering.
- `python/tests/check_file_size/test_file_collector.py` — new cases.
