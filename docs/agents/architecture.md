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

### Command entrypoint convention

Every command's entry point is `<language>/<command>/main.<extension>` (e.g.
`python/check_file_size/main.py`, `shell/install/main.sh`) — this is the file
`commands/*.json`'s `path` field points at, and the only thing `bin/tingle`
dispatches to.

- `main.<ext>` is a thin dispatcher, never invoked directly by the user with
  raw command args: `bin/tingle` (or the completion hub) always prepends a
  leading flow verb, `run` or `complete`, as argv[1] / `$1`. `main.<ext>`
  reads that verb and forwards the rest of argv (argv[2:]) to either:
  - the executor, `<command>/executor.<ext>`, for `run`; or
  - the completion handler, `<command>/completion.<ext>`, for `complete`.
- Completion is opt-in per command. The completion hub (see `completions/`
  below) detects support by checking whether `completion.<ext>` exists next
  to a command's `main.<ext>` — it never invokes `main.<ext> complete` to
  probe for support. Commands without a `completion.<ext>` (e.g.
  `check_file_size`, `install`) get the hub's generic native file/folder
  completion fallback instead.
- A completion handler receives raw argv, including a possibly-empty
  trailing element for the word currently being typed, and must not run it
  through a strict parser (e.g. `argparse`) — that trailing empty string is
  significant and would break/be rejected by a strict parser.

### Breaking a command down once it outgrows a single file

Most Python (and other language) scripts stay a single file for their
executor. Once a command's logic grows too large for one file, break it down
following this pattern instead of inventing a one-off structure:

- The executor (`executor.<ext>`) stays a thin shell: parse args, instantiate
  the orchestrator class, call it, exit.
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
it splits into `main.py` (the `run`/`complete` dispatcher), `executor.py`
(holds the `CheckFileSize` orchestrator class), `constants.py`,
`skip_checks.py`, `file_collector.py`, `file_analyzer.py`, and `reporter.py`.

#### Test folder location

Tests for `python/` live under `python/tests/`, mirroring the package layout
under `python/` (e.g. `python/tests/check_file_size/`,
`python/tests/common/`), rather than a top-level `tests/`. Future Python
commands under this repo should follow the same pattern.

### `bin/`

Callable entry points intended to be placed on `PATH`. Each file here is a
thin wrapper that dispatches to the actual implementation in `shell/`,
`python/`, or `node/` — this is the only folder users should invoke directly.

### `completions/`

Holds the bash completion scripts for `tingle`:

- `completions/tingle.bash` — central hub, sourced from `~/.bashrc` by
  `tingle install`. Sources the two files below and registers the
  `complete -F` dispatcher for the `tingle` command.
- `completions/bash/tingle.sh` — level-one completion: command names (reads
  `commands/*.json`).
- `completions/bash/commands.sh` — level-two completion: command-specific
  arguments. Delegates to a command's own `completion.<ext>` via
  `tingle resolve <cmd>` when one exists, or falls back to native
  file/folder completion (`compgen -f` + `compopt -o filenames`) otherwise.

### `.circleci/`

Holds the CI pipeline config (`.circleci/config.yml`). Owned by `architect`,
since CI is cross-cutting rather than belonging to a single language
specialist.

## Conventions

- Each script is self-contained: no shared internal library or cross-script
  imports unless a clear, recurring need arises.
- Each script documents its own usage and dependencies in a header comment.
- New scripts are registered in the table in `README.md`.
