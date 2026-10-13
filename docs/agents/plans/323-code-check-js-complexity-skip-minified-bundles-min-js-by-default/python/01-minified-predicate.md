# Add the minified constant and predicate

Add `MINIFIED_SUFFIXES: ClassVar[tuple[str, ...]] = (".min.js", ".min.mjs", ".min.cjs")` to `Constants`, next to `DECLARATION_SUFFIXES`, with a comment like the existing ones (skipped by default unless `no_default_excludes`, matched on the lower-case name).

In `selection.py`, add `is_minified(path: Path) -> bool` next to `is_declaration` (`path.name.lower().endswith(Constants.MINIFIED_SUFFIXES)`) and export it in `__all__`.

Give `js_complexity.selection.select_files` a keyword argument `skip_minified: bool = True`. Build the `skip` predicate passed to `docker_check_selection.select_files`: `is_declaration` always, plus `is_minified` when `skip_minified` is true (declaration first, then minified, per filter order step 6). Update the module docstring and the `select_files` docstring to mention the minified skip.

Because `skip` is applied after `FileCollector.collect` for both directory and single-file targets, a minified single-file `<path>` is skipped too and `--include` cannot bring it back — no extra code is needed for those rules; just verify it.

## Files to Change
- `python/code_check/js_complexity/constants.py` — add `MINIFIED_SUFFIXES`.
- `python/code_check/js_complexity/selection.py` — add `is_minified`, the `skip_minified` parameter and the combined predicate; docstrings.
