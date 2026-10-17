# Use the merged selection options in the executor
Replace the placeholder `CheckPhpComplexity._selection_options` with an override that extends the base one, the way `CheckJsComplexity` adds `skip_minified`:

```python
@classmethod
def _selection_options(cls, options: dict) -> dict:
    """Extend the base selection options with the `bootstrap/cache` skip.

    The `bootstrap/cache` rule applies unless `no_default_excludes` is set.
    """
    return {
        **super()._selection_options(options),
        "skip_bootstrap_cache": not bool(options.get("no_default_excludes")),
    }
```

Check that `LIST_KEYS = ("ignore", "include")` and `_merge` already carry `exclude`, `ignore`, `include`, `no_default_excludes` and `gitignore` through, and fix whatever doesn't. Update the module docstring: the file-selection paragraph (list the flags and drop the "no selection flags, no `.gitignore` filtering" sentence, but keep "no config file yet") and the Examples block (`--exclude tests,fixtures`, `--no-default-excludes --exclude vendor`, `--ignore 'tests/**'`, `--include 'src/**'`, `--no-gitignore`). In `selection.py`, update the `select_files` docstring, which says `gitignore` is "off by default until the selection flags land".

## Files to Change
- `python/code_check/php_complexity/executor.py` — the `_selection_options` override and the module docstring.
- `python/code_check/php_complexity/selection.py` — the docstring wording about `gitignore`.
