# Add pinned dev dependencies

Create `python/requirements-dev.txt`, pinning exact versions (not floating
ranges, per the issue's Performance & Security decision) for the dev-only
tools the test suite and CI need:

```
pytest==8.3.4
pytest-cov==6.0.0
ruff==0.16.4
```

`ruff==0.16.4` matches the version already used locally (per
`python/.ruff_cache`) so CI lints with the same version as local dev — ruff
had no pinned version anywhere before this (it was only ever invoked
ad hoc). No runtime dependencies exist to pin (`check_file_size` and
`ArgParser` are stdlib-only), so this file only ever needs dev tools.

## Files to Change

- `python/requirements-dev.txt` — new file, pinned `pytest`, `pytest-cov`,
  `ruff` versions as shown above.
