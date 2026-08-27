# Architecture

## Overview

Tingle is a flat collection of independent, single-purpose utility scripts —
there is no shared application runtime or framework. Each script solves one
recurring task on its own, in whichever language is the best fit (Bash,
Python, or Node.js).

## Source Code Layout

There is no single main source folder; scripts are grouped by language:

### `shell/`

Bash/Shell scripts. Best fit for simple file/OS-level operations and gluing
together other CLI tools.

### `python/`

Python scripts. Best fit for tasks needing richer data manipulation, parsing,
or third-party libraries.

### `node/`

Node.js scripts. Best fit for tasks that benefit from the npm ecosystem
(e.g. working with JSON/APIs).

### Breaking a command down once it outgrows a single file

Most Python (and other language) scripts stay a single file. Once a
command's logic grows too large for one file, break it down following this
pattern instead of inventing a one-off structure:

- Commands are still registered in `commands/*.json`, pointing at their
  implementation entry point; `bin/tingle` remains the single hub that
  dispatches to it — this never changes.
- The command's entry point stays a thin shell: parse args, instantiate the
  orchestrator class, call it, exit.
- Reusable/common code (e.g. the generic argument parser) lives in
  `python/common/` (or the equivalent `<lang>/common/` folder), not inside
  the command's own package.
- Argument parsing goes through the shared `ArgParser`
  (`python/common/arg_parser.py`):
  - `ArgParser(flags: list[dict])` — `flags` is a list of dicts shaped like
    `argparse.add_argument`'s kwargs plus a `"name"` key for the flag string,
    e.g. `{"name": "--warn", "type": int, "default": 300, "help": "..."}`.
  - `.parse(argv: list[str] | None = None) -> dict` — parses (defaulting to
    `sys.argv[1:]`) and returns a plain `dict` of option name → value (not an
    `argparse.Namespace`).
  - Command-specific code only supplies its flag list and calls
    `ArgParser(flags).parse()`, instead of building its own
    `argparse.ArgumentParser`.
- Beyond arg parsing, a command breaks its own logic down by class/file as
  needed: it becomes a package under `python/<command>/` (package-style,
  `__init__.py` + one file per class), with the orchestrator class named
  after the command.

`python/check_file_size/` is the first example of this pattern in practice:
it splits into `constants.py`, `skip_checks.py`, `file_collector.py`,
`file_analyzer.py`, `reporter.py`, and `check_file_size.py`, which holds the
`CheckFileSize` orchestrator class (the entry point that `commands/*.json`
still points at).

### `bin/`

Callable entry points intended to be placed on `PATH`. Each file here is a
thin wrapper that dispatches to the actual implementation in `shell/`,
`python/`, or `node/` — this is the only folder users should invoke directly.

### `completions/`

Holds the bash completion script(s) for `tingle`, namely
`completions/tingle.bash`. This script is sourced from `~/.bashrc` by
`tingle install`.

## Conventions

- Each script is self-contained: no shared internal library or cross-script
  imports unless a clear, recurring need arises.
- Each script documents its own usage and dependencies in a header comment.
- New scripts are registered in the table in `README.md`.
