# Wire selection and executor

- `select_files(target, root, *, excludes, ignore, include, gitignore)` builds
  `FileCollector(excludes, [".rb"], ignore=..., include=..., gitignore=...,
  binary_check=False, outside_symlinks=False)`.
- `build_selection` maps each file to `path.resolve().relative_to(root)` so a kept
  symlink becomes its target's relative path (this also makes absolute symlinks
  pointing inside `<path>` work), deduplicates by resolved path, then keeps the
  existing unsendable-name warning and sort.
- The executor resolves options: `excludes = resolve_excludes(Constants.DEFAULT_EXCLUDES,
  parse_excludes(exclude), no_default_excludes)`, `ignore`/`include` default to
  `[]`, `gitignore = not no_gitignore`; `_select` passes them to `select_files`.
  Add usage examples to the module docstring.

## Files to Change
- `python/code_check/rubycritic/selection.py` — new options, outside_symlinks=False, resolve + dedup.
- `python/code_check/rubycritic/executor.py` — option resolution and pass-through.
