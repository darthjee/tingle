# Plan: Execution: sed subcommand

Issue: [38-execution--sed-subcommand.md](../../issues/38-execution--sed-subcommand.md)

## Overview

Wire the `sed` subcommand into `tingle linux`, forwarding all arguments
verbatim to GNU `sed` inside the `tingle-linux` container. `shell/linux/docker_run.sh`'s
current interactive flag only supports full `-it` or neither, so it also
gets a new stdin-only mode (attach stdin, no TTY) so piped usage like
`cat file | tingle linux sed 's/a/b/'` works. `commands/shell.json`'s
`long_help` gets updated to document the new subcommand and its
piped-stdin usage.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)

## Shared contracts

- Subcommand name and invocation: `tingle linux sed <sed-args...>` —
  arguments are forwarded verbatim to `sed` inside the container, no
  parsing/validation of `sed`'s own flags.
- Piped-stdin usage works: `cat file | tingle linux sed 's/a/b/'`.
- In-place edit example: `tingle linux sed -i 's/foo/bar/' somefile.txt`
  (GNU `-i` syntax — no backup-suffix argument, unlike BSD `sed`).

`cli`'s `commands/shell.json` `long_help` update must describe exactly
this invocation and these examples — it documents `shell`'s
implementation, not the other way around.
