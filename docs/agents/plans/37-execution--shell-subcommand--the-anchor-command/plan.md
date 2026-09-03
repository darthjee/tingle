# Plan: Execution: shell subcommand (the anchor command)

Issue: [37-execution--shell-subcommand--the-anchor-command.md](../../issues/37-execution--shell-subcommand--the-anchor-command.md)

## Overview

Implement `tingle linux shell` by replacing its stub handler with a call to
the existing `docker_run` helper, launching an interactive `bash` session in
the `tingle-linux` container with the current directory mounted. Add a
matching usage example to the command's `--help` text.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)

## Shared contracts

- Invocation surface: `tingle linux shell` takes no arguments and starts an
  interactive shell — `cli`'s usage example in `commands/shell.json`'s
  `linux.long_help` must show exactly `tingle linux shell` (no flags/args),
  matching what `shell`'s `_handle_shell` implements.
