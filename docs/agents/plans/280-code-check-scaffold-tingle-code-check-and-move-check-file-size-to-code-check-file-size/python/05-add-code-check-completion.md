# Add code_check completion
Create `python/code_check/completion.py` with `complete(argv: list[str]) -> list[str]`, following
`python/kube/completion.py`. `argv` is the raw word list after `code_check`, and its last element is the word being
typed (possibly `""`). Split it into `committed = argv[:-1]` and `current = argv[-1] if argv else ""`. Scan
`committed` by position without argparse, and return the full candidate set with no prefix filtering. Import only
`code_check.file_size.flags.FLAGS` plus the subcommand names, never `code_check.executor`, which would pull in the
collector, config and reporter. Keep the names in a small import-light module that both the executor and completion
read, e.g. a `SUBCOMMAND_NAMES` tuple in `code_check/subcommands.py`, and have `CodeCheck.SUBCOMMANDS` use the same
keys. Derive
everything else from `FLAGS`: flag names, `action` (`store_true`/`append`) and `choices`.

The rules match the issue's Completion table:
- No committed words, or the committed words are only `-h`/`--help`: return the subcommand names.
- `committed[0]` is another flag, or an unknown subcommand: return `[]`.
- Inside `file_size`, look at the last committed word after the subcommand:
  - It is a flag with `choices` (`--min-level`, `--fail-on`): return those choices.
  - It is a flag that takes any other value: return `[]`.
  - It is a `store_true` flag, or nothing flag-related applies: fall through to the position rules below.
- Position rules: if `current` starts with `-`, return every flag name. If no positional path has been given yet,
  return `["__tingle_files__"]`. Otherwise return every flag name. Flags already used are still suggested.
- No config read, no `git`, no filesystem access and no network.

Tests: add `python/tests/code_check/test_completion.py` with one test per table row. Also assert that the flag list
and the choices returned equal what is derived from `FLAGS`, so they can't drift, and that the file sentinel is never
mixed with words.

## Files to Change
- `python/code_check/completion.py` — new.
- `python/code_check/subcommands.py` — new, import-light `SUBCOMMAND_NAMES`.
- `python/code_check/executor.py` — keep `SUBCOMMANDS` keys in sync with `SUBCOMMAND_NAMES`.
- `python/tests/code_check/test_completion.py` — new.
