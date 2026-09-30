# Issue: code_check: deprecation warning on tingle check_file_size alias

## Description
Part of #279. Follows #280 (merged), which turned `tingle check_file_size` into a shim (`python/check_file_size/main.py`) that forwards `run` to `code_check.file_size.executor.CheckFileSize`. This issue makes the old name a visibly **deprecated** alias of `tingle code_check file_size`.

## Problem
Users and CI scripts still calling `tingle check_file_size` get no sign that the command has moved. Without that, the alias can never be removed safely.

## Expected Behaviour
- `tingle check_file_size ...` prints, on stderr, before anything else:
  `Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.`
  It is yellow via `Palette(sys.stderr)` (`python/code_check/palette.py`), so it is uncoloured when stderr is not a TTY or `NO_COLOR` is set.
- After the warning, the command behaves exactly like `tingle code_check file_size ...`. Stdout is unchanged, and exit codes 0, 1 and 2 are forwarded unchanged.
- The warning is also printed when the shim shows help (no arguments, or `--help` after the command name, both of which reach the shim's `run` flow).
- `tingle code_check file_size` never prints the warning.
- `tingle help` shows `check_file_size` with a short help starting with `Deprecated: use code_check file_size.`
- `tingle --help check_file_size` is answered by the hub from `commands/python.json` and never reaches the shim, so it prints no stderr warning. Its long help is itself the deprecation notice (see Solution).
- Tab completion is unchanged: the shim still has no `complete` flow, so `tingle check_file_size <TAB>` keeps the hub's file/folder completion and never prints the warning.

## Solution
- `python` agent:
  - `python/check_file_size/main.py` prints the warning on `run` only, then forwards. Do not add a `complete` flow.
  - Tests in `python/tests/check_file_size/test_main.py`:
    - the warning goes to stderr only;
    - stdout is identical to calling `CheckFileSize` directly;
    - exit codes 0, 1 and 2 are forwarded;
    - no colour when stderr is not a TTY.
- `cli` agent: in `commands/python.json`, for `check_file_size`:
  - `short_help` starts with `Deprecated: use code_check file_size.`;
  - `long_help` is replaced by a short pointer of 2–3 lines: the command is deprecated, use `tingle code_check file_size`, see `tingle --help code_check`. The duplicated full body and its stale `./check_file_size.py` examples are removed.
- `guide` agent:
  - add a "Migrating from `check_file_size`" note to `docs/guides/code_check.md`: the rename, the alias still works but prints a deprecation warning on stderr, and it will be removed in a future release (no version named);
  - update `docs/guides/check_file_size.md` (it now says the old name "behaves the same way") to mention the stderr deprecation warning and link the migration note.

## Out of scope
- Removing the alias.
- Renaming the `check_file_size` config section (#282) and cleaning up other stale mentions (#283).

## Verification
- `cd python && ruff check . && pytest`.
- `bin/tingle check_file_size . 2>/dev/null` gives the same stdout as `bin/tingle code_check file_size .`, and `bin/tingle check_file_size . >/dev/null` shows the warning.
- `bin/tingle help` lists `check_file_size` as `Deprecated: use code_check file_size. ...`.

## Benefits
Users get a clear migration path before the alias is eventually removed.
