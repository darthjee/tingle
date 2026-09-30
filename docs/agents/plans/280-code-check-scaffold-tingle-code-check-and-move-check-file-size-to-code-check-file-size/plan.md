# Plan: code_check: scaffold tingle code_check and move check_file_size to code_check file_size

Issue: [280-code-check-scaffold-tingle-code-check-and-move-check-file-size-to-code-check-file-size.md](../../issues/280-code-check-scaffold-tingle-code-check-and-move-check-file-size-to-code-check-file-size.md)

## Overview
This adds a new `tingle code_check` command. Its first and only subcommand is `file_size`, and it is backed by the existing
`check_file_size` code, which is moved (`git mv`) to `python/code_check/file_size/`. A static-dict dispatcher
(`CodeCheck`) and a side-effect-free `completion.py` sit at `python/code_check/`.
`tingle check_file_size` stays as a thin shim with unchanged behaviour and no warning. The CLI registration, user
guides and agent docs are updated to match, and the architect updates the root `README.md` and `.claude/agents/guide.md`.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Entry point:** `python/code_check/main.py` (mode 100755, shebang). `bin/tingle` runs it as
  `main.py run <args...>` / `main.py complete <words...>`. `sys.argv[1]` is the flow verb and `sys.argv[2:]` are the
  user's words after `code_check`.
- **Completion:** `python/code_check/completion.py` must exist next to `main.py`, because the hub only calls
  `complete` when it does. `complete(argv) -> list[str]` gets the raw words after `code_check`, including the word
  being typed, and returns either a word list or exactly `["__tingle_files__"]`, never both. It does no prefix
  filtering.
- **`commands/python.json`:** new key `code_check` with
  `{"path": "python/code_check/main.py", "short_help": ..., "long_help": ...}`. The `check_file_size` entry stays
  unchanged, still pointing at `python/check_file_size/main.py`.
- **Subcommand table:** `SUBCOMMANDS = {"file_size": (CheckFileSize, "<one-line description>")}`, or an equivalent
  name → class + description mapping. Names are exact: no case folding and no `file-size` alias.
- **Messages and exit codes (`CodeCheck.run`):**
  - No args, `-h` or `--help`: list the subcommands, then
    `Run 'tingle code_check <subcommand> --help' for its options.`, exit 0.
  - `-h <sub>` / `--help <sub>`: forwarded as `<sub> -h`.
  - Unknown subcommand: `Error: unknown subcommand '<x>'` (red, stderr) plus the list, exit 1.
  - A flag before the subcommand: `Error: expected a subcommand before options (got '<flag>')` (red, stderr) plus the
    list, exit 1.
  - `file_size` exit codes are forwarded unchanged: 0, 1, and 2 for `--fail-on`.
- **Help prog:** `file_size` help reads `usage: tingle code_check file_size ...`. The `check_file_size` shim shows the
  same prog, which is acceptable for a pure move.
- **Config:** the path is unchanged (`~/.tingle/code_check/config.json`), and the section name stays `check_file_size`
  in this issue.
- **Guide paths:** `docs/guides/code_check.md` (overview), `docs/guides/code_check/file_size.md` (moved guide), and
  `docs/guides/check_file_size.md` (stub). The root `README.md` and `long_help` link or refer to these.

## Coordinator (architect) work

The coordinator's own scope is not a specialist split, so the architect does this work after the specialists finish:

- `README.md`, Scripts table: add a `code_check` row linking `docs/guides/code_check.md` ("Code evaluation checks;
  first subcommand `file_size`: ..."). Change the `check_file_size` row to "Moved to `code_check file_size`",
  linking the stub. Add a short mention of subcommand-style commands (`tingle code_check <subcommand>`) in the
  Commands section. It has no existing `check_file_size` entry.
- `.claude/agents/guide.md`: update the scope and Conventions so that a command with subcommands may have a
  `<command>.md` overview plus `<command>/<subcommand>.md` pages. Replace the `check_file_size.md` example with
  `code_check.md`.
- Integration check: the `commands/python.json` `path` matches the real executable `python/code_check/main.py`, and the
  issue's Verification steps pass. These include identical output from `bin/tingle code_check file_size .` and
  `bin/tingle check_file_size .`, the listing from `bin/tingle --help code_check`, and bash completion rows.
