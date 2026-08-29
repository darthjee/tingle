# Add kube to the coverage source list

`python/pyproject.toml`'s `[tool.coverage.run]` only lists `source = ["check_file_size", "common"]`, so `python/kube/` isn't measured by the `--cov-fail-under=75` gate at all — a gap left over from #20. This issue is the first to add real branching logic (pass-through vs. resolved alias, pre-check success vs. failure, switch validated vs. not) worth enforcing coverage on, so close the gap here.

## Files to Change

- `python/pyproject.toml` — add `"kube"` to `[tool.coverage.run]`'s `source` list.
