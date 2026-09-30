# Python Plan: code_check: deprecation warning on tingle check_file_size alias

Main plan: [plan.md](plan.md)

## Shared contracts

- Print exactly `Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.` to stderr, wrapped in `Palette(sys.stderr).YELLOW`/`.RESET` (`python/code_check/palette.py`), before calling `CheckFileSize().run(args)`.
- Only in the `run` flow. Do **not** add a `complete` flow, so the hub keeps its file/folder completion.

## Implementation Steps

### Step 1 — Print the warning in the shim
In `python/check_file_size/main.py`, when `flow == "run"`, print the coloured warning to `sys.stderr` (e.g. `print(f"{p.YELLOW}{WARNING}{p.RESET}", file=sys.stderr)` with `p = Palette(sys.stderr)` and a module-level `WARNING` constant), then call `CheckFileSize().run(args)` as today. `CheckFileSize.run` calls `sys.exit(0|1|2)` itself, so exit codes forward unchanged; do not catch `SystemExit`. Update the module docstring to say the alias is deprecated and warns on stderr, and keep the "no `complete` flow on purpose" note.

### Step 2 — Tests
In `python/tests/check_file_size/test_main.py`:
- Update `test_main_dispatches_run_flow_with_remaining_args`: it now asserts `err == ""`, which must become "err is exactly the warning line".
- Add tests:
  - the warning goes to stderr only, and stdout from a fake `CheckFileSize` that prints is unchanged;
  - using the real `CheckFileSize` on a small `tmp_path` tree, stdout equals a direct `CheckFileSize().run(...)` call;
  - `SystemExit` codes 0, 1 and 2 raised by the executor reach the caller unchanged (`pytest.raises(SystemExit)` with a fake that calls `sys.exit(n)`);
  - with a captured (non-TTY) stderr, or `NO_COLOR=1`, the warning has no `\033[` escape;
  - with a TTY stub (`isatty` → True) and `NO_COLOR` unset, it is wrapped in yellow;
  - the `complete` and unknown-flow paths print no warning.

## Files to Change
- `python/check_file_size/main.py` — print the deprecation warning on `run`; update the docstring.
- `python/tests/check_file_size/test_main.py` — adjust the existing stderr assertion and add the tests above.

## CI Checks
- `python`: `cd python && ruff check . && pytest` (CircleCI jobs: lint, tests)

## Notes
- Keep the D212 docstring style (summary on the first line) used across `python/`.
- Watch the test path: `sys.path` handling in `main.py` must keep working when imported from tests.
