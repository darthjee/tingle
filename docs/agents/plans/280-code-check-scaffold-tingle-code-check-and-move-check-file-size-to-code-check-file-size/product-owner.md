# Product-owner Plan: code_check: scaffold tingle code_check and move check_file_size to code_check file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- Layout after the python work:
  - `python/code_check/` holds `main.py`, `executor.py` (`CodeCheck` with a static `SUBCOMMANDS` dict),
    `completion.py`, `palette.py` (`Palette` plus `Colors`) and `config.py` (generic `default_path`/`load_section`/
    `ConfigError`).
  - `python/code_check/file_size/` holds the moved check (plus the new `flags.py`).
  - `python/check_file_size/` is a shim (`__init__.py`, `main.py`).
- Tests move to `python/tests/code_check/` and `python/tests/code_check/file_size/`. `python/tests/check_file_size/`
  keeps only the shim test.
- `ArgParser(flags, prog=None)` gains an optional `prog`.
- Dispatcher exit codes: 0 for help, 1 for unknown or misplaced input, and 2 reserved for check gates such as `--fail-on`.

## Implementation Steps

### Step 1 — Update docs/agents/architecture.md
- L42, entrypoint example: `python/check_file_size/main.py` → `python/code_check/main.py`.
- L55-57, completion opt-in: the fallback example becomes the `check_file_size` alias (or just `install`). Add a
  note that `code_check`'s completion returns `__tingle_files__` for the path position and flag names when the word
  being typed starts with `-`.
- L78-89, `ArgParser` API: document the optional `prog` argument.
- L97-100, "first example of this pattern": point at `python/code_check/file_size/`, and refresh the file list
  (`config.py`, `glob_matcher.py`, `git_ignore.py`, `flags.py`, with `palette.py`/generic `config.py` at
  `code_check/`). Add a subsection on subcommand dispatch covering:
  - the `CodeCheck` static `SUBCOMMANDS` dict, with no argparse subparsers;
  - `args[0]` looked up and `args[1:]` forwarded;
  - the exit codes;
  - the "move a helper up only once a second consumer needs it" rule;
  - the `check_file_size` shim.
- L136, test folder example: `python/tests/check_file_size/` → `python/tests/code_check/file_size/`.

### Step 2 — Optional touch-ups
In `docs/agents/specs.md` L26, the folder-name example may become `code_check`. It is fine to leave it.
`folder-structure.md`, `flow.md` and `contributing.md` have no references.

## Files to Change
- `docs/agents/architecture.md` — paths, dispatcher description, `ArgParser` `prog`.
- `docs/agents/specs.md` — optional example tweak.
