# Match excludes on the relative path

`FileCollector._is_excluded` checks `path.parts`, which is the absolute path. Components
of `<path>` and its parents then count, so a project under `~/work/build/app` has every
file excluded.

- Change `_is_excluded` to take the path relative to the target (e.g.
  `_is_excluded(rel: Path)`, or pass `path.relative_to(target)`), and check its `parts`.
- In `collect`, compute `rel = path.relative_to(target)` once per file and reuse it for
  both `_is_excluded(rel)` and `_accepts(path, rel.as_posix())`.
- The single-file branch stays as is: no path-component exclude check.
- Update the `__init__` docstring to say that `excludes` are whole path-component names
  matched relative to the target.

## Files to Change
- `python/check_file_size/file_collector.py` — `collect`, `_is_excluded`, docstring.
