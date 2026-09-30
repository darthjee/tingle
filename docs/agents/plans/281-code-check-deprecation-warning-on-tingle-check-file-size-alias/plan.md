# Plan: code_check: deprecation warning on tingle check_file_size alias

Issue: [281-code-check-deprecation-warning-on-tingle-check-file-size-alias.md](../../issues/281-code-check-deprecation-warning-on-tingle-check-file-size-alias.md)

## Overview
Make `tingle check_file_size` a visibly deprecated alias of `tingle code_check file_size`. The shim prints a yellow stderr warning on `run`, then forwards unchanged. The hub help (`commands/python.json`) marks the command as deprecated, and the user guides explain the migration. Behaviour, stdout, exit codes and tab completion stay the same.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- **Warning text** (exact, one line, on stderr, before any other output):
  `Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.`
  The python agent prints it wrapped in `Palette(sys.stderr).YELLOW` … `.RESET`, so it is plain when stderr is not a TTY or `NO_COLOR` is set. The guide agent quotes the plain text.
- **When the warning appears**: only in the shim's `run` flow. That covers `tingle check_file_size <args>`, `tingle check_file_size` with no args, and `tingle check_file_size --help`. It never appears for `tingle --help check_file_size` (answered by the hub from JSON), for tab completion (the shim has no `complete` flow), or for `tingle code_check file_size`.
- **short_help prefix** (exact): `Deprecated: use code_check file_size.`
- **Removal wording**: "will be removed in a future release". No version is named.
