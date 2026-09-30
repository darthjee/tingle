# Python Plan: code_check: scaffold tingle code_check and move check_file_size to code_check file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- You produce `python/code_check/main.py` (100755, shebang). It handles `run` (→ `CodeCheck().run(sys.argv[2:])`) and
  `complete` (→ `print(" ".join(complete(sys.argv[2:])))`), mirroring `python/kube/main.py:19-25`.
- You produce `python/code_check/completion.py` with `complete(argv: list[str]) -> list[str]`. It returns either a word
  list or exactly `["__tingle_files__"]`, and does no prefix filtering.
- `CodeCheck.run` messages and exit codes are exactly as listed in [plan.md](plan.md#shared-contracts): 0 for help, 1 for
  unknown/misplaced input, and `file_size` codes forwarded unchanged.
- `file_size` help prog is `tingle code_check file_size`.
- The config path and the `check_file_size` section name are unchanged.
- `python/check_file_size/main.py` remains the target of the unchanged `check_file_size` entry in
  `commands/python.json`.

## Steps

- [01 — Move the package and tests](python/01-move-package-and-tests.md)
- [02 — Extract shared helpers and FLAGS](python/02-extract-shared-helpers-and-flags.md)
- [03 — Add prog to ArgParser](python/03-add-prog-to-arg-parser.md)
- [04 — Add the code_check dispatcher](python/04-add-code-check-dispatcher.md)
- [05 — Add code_check completion](python/05-add-code-check-completion.md)
- [06 — Add the check_file_size shim](python/06-add-check-file-size-shim.md)

## CI Checks
- `python/`: `cd python && ruff check .` (CI job: `lint`)
- `python/`: `cd python && pytest` with coverage at or above 75% (CI job: `tests`). Alternatively run `make tests`.

## Notes
- Codacy tracks findings by path, so triaged findings may reappear as "new" after `git mv`. Do not fix them in this PR.
- Keep the `# nosec` annotations in `git_ignore.py` as they are.
- Completion must not read config, call `git`, walk the filesystem or import the executor, collector, config or
  reporter. It may import only `code_check.file_size.flags`.
- `SUBCOMMANDS` is a static dict. User input is only used as a dict key, never passed to `importlib`, `getattr` on
  modules, or `eval`.
- Stale text you may clean while you are there: the docstrings in the executor, palette and constants (which say
  `./check_file_size.py` or `check_file_size.palette`), `kube/parser.py:6`, and `tests/common/test_arg_parser.py:13`
  and `:63`.
