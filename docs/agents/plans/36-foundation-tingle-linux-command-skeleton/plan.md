# Plan: Foundation: tingle linux command skeleton

Issue: [36-foundation-tingle-linux-command-skeleton.md](../issues/36-foundation-tingle-linux-command-skeleton.md)

## Overview

Adds the dispatch scaffolding for `tingle linux` (parent #34): a
`shell/linux/main.sh`/`executor.sh` pair following the existing flow-verb
dispatcher convention, a shared `docker_run.sh` helper implementing the
agreed container-invocation model, and a `linux` entry in
`commands/shell.json` so `bin/tingle` can resolve it. `shell`/`sed` get
no-op stub handlers wired into the dispatch map to prove it end-to-end; real
behavior lands in #37/#38.

## Agents involved

- [shell](shell.md)
- [cli](cli.md)

## Shared contracts

- **Command name**: `linux`.
- **Entry point path**: `shell/linux/main.sh` — this is the exact `path`
  value `cli` writes into the new `commands/shell.json` entry.
- **Subcommands surfaced to the user** (both stubbed in this issue, real
  behavior in #37/#38): `shell` (interactive container shell) and `sed`
  (forwards args to GNU `sed` in the container). `cli`'s `short_help`/
  `long_help` text for the `linux` entry should describe these two
  subcommands, following the descriptive style already used for the `kube`
  entry in `commands/python.json`.
- No `completion.sh` is added in this issue (out of scope) — `cli` does not
  need to special-case `linux` in its completion dispatch; it falls back to
  the existing generic file/folder completion.

## Notes

- README.md's Script table (root-level, owned by `architect`) should gain a
  `linux` row (Shell) once this lands — the architect updates it directly
  during integration rather than through either specialist plan file.
