# Add the code_check dispatcher
- `python/code_check/main.py` (new, mode 100755, `#!/usr/bin/env python3`): insert `python/` into `sys.path` the same
  way `kube/main.py` does, then dispatch on `flow = sys.argv[1]`. `run` calls `CodeCheck().run(sys.argv[2:])`, and
  `complete` calls `print(" ".join(complete(sys.argv[2:])))`. Copy the shape of `python/kube/main.py:19-25`.
- `python/code_check/executor.py` (new): a `CodeCheck` class with a static
  `SUBCOMMANDS = {"file_size": (CheckFileSize, "Token efficiency triage: file size analysis.")}`, or a small
  record/dict holding the class and a description. `CheckFileSize` is imported eagerly. `run(args)` works as follows:
  - Empty args, `["-h"]` or `["--help"]`: print the subcommand list (name plus one-line description), then
    `Run 'tingle code_check <subcommand> --help' for its options.`, and exit 0.
  - `args[0]` in `("-h", "--help")` followed by a subcommand: forward as `[sub, "-h", *rest]`. The subcommand prints its
    help and exits 0. An unknown name after `-h` is handled as an unknown subcommand.
  - `args[0]` starts with `-` (any other flag): write `Error: expected a subcommand before options (got '<flag>')` in
    red on stderr (`Palette(sys.stderr)`), then the list, and exit 1.
  - `args[0]` not in `SUBCOMMANDS`, an exact match with no case folding or hyphen alias: write
    `Error: unknown subcommand '<x>'` in red on stderr, then the list, and exit 1.
  - Otherwise call `SUBCOMMANDS[args[0]]` → `cls().run(args[1:])`, letting its `SystemExit` codes (0/1/2) propagate
    unchanged.
  - Use a plain dict lookup, not argparse subparsers, so `CheckFileSize` keeps its own `ArgParser(FLAGS)` and the
    `_parse` exit-code mapping.
- Tests: add `python/tests/code_check/test_executor.py` covering every row of the issue's Edge cases table. That means
  no args, `-h`, `--help`, `-h file_size`, `--help file_size`, `file_size -h`, `file_size` with no path (help, exit 0),
  a misplaced `--warn 100 file_size .`, `File_Size`, `file-size`, and an unknown name. It also checks that exit codes
  0, 1 and 2 (`--fail-on`) are forwarded, and that red codes appear on stderr only when colour is enabled. Add
  `python/tests/code_check/test_main.py` covering the `run` and `complete` branches by monkeypatching `CodeCheck` and
  `complete` on the module, as the old `test_main.py` did.

## Files to Change
- `python/code_check/main.py` — new entry point (100755).
- `python/code_check/executor.py` — new `CodeCheck` dispatcher.
- `python/tests/code_check/test_executor.py`, `python/tests/code_check/test_main.py` — new tests.
