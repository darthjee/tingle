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

### `bin/`

Callable entry points intended to be placed on `PATH`. Each file here is a
thin wrapper that dispatches to the actual implementation in `shell/`,
`python/`, or `node/` — this is the only folder users should invoke directly.

## Conventions

- Each script is self-contained: no shared internal library or cross-script
  imports unless a clear, recurring need arises.
- Each script documents its own usage and dependencies in a header comment.
- New scripts are registered in the table in `README.md`.
