# Unit tests: ArgParser

Cover `python/common/arg_parser.py`'s `ArgParser` (`build()`/`parse()`).
Reuse `check_file_size`'s own flag shapes (`_flags()` in
`check_file_size.py`) as realistic fixtures rather than inventing unrelated
ones, since that's the only real consumer today.

Cases:
- A simple positional + a typed optional flag (`type=int`, `default=...`)
  parses a given `argv` list into the expected `dict` (not an
  `argparse.Namespace`).
- Default values are used when a flag is omitted from `argv`.
- `action="append"` flag (mirroring `--ext`) accumulates repeated
  occurrences into a list; stays `None`/absent default when never passed.
- `parse()` with no `argv` argument falls back to `sys.argv[1:]` (patch
  `sys.argv` in the test).
- `build()` returns a usable `argparse.ArgumentParser` instance (e.g.
  `.print_help()` doesn't raise).

## Files to Change

- `python/tests/common/__init__.py` — new, empty (package marker, matching
  `python/common/__init__.py`'s convention).
- `python/tests/common/test_arg_parser.py` — new, cases above.
