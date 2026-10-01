# Add outside_symlinks to FileCollector

Add a keyword-only `outside_symlinks: bool = True` argument (after
`binary_check`) to `FileCollector`. When `False`, apply step 6 last, after
`_accepts`, in both the directory walk and `_collect_file`: drop a file whose
`path.resolve()` is not inside the resolved root (`target.resolve()` for a
directory, `target.parent.resolve()` for a single file). This covers outside
targets and dangling links. The collector keeps returning the link path; filters
still run on the link's own relative path. Default `True` keeps `file_size`
unchanged. Update the docstring.

## Files to Change
- `python/code_check/file_size/file_collector.py` — new argument, step 6 helper, docstring.
