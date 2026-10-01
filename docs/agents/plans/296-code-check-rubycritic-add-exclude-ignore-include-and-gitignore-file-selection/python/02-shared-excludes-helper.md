# Share the excludes helper

Move the logic of `CheckFileSize._parse_excludes` (comma split, drop blanks) and
`_resolve_excludes` (defaults unless `--no-default-excludes`, plus extras,
deduplicated with `dict.fromkeys`) into a light module with
`parse_excludes(raw)` and `resolve_excludes(defaults, extra, no_default_excludes)`.
Keep the `CheckFileSize` staticmethods as thin wrappers passing `file_size`'s
`Constants.DEFAULT_EXCLUDES`, so its tests stay unchanged. Do not import the new
module from `flags.py` or `completion.py`.

## Files to Change
- `python/code_check/excludes.py` — new module with the two functions.
- `python/code_check/file_size/executor.py` — wrappers delegate to the new module.
