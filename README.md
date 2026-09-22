# Tingle

Personal repository of everyday utility scripts — a code "Swiss Army knife".

[![Build Status](https://circleci.com/gh/darthjee/tingle.svg?style=shield)](https://circleci.com/gh/darthjee/tingle)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/aed499abf82847498ae54673db8f348c)](https://app.codacy.com/gh/darthjee/tingle/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/aed499abf82847498ae54673db8f348c)](https://app.codacy.com/gh/darthjee/tingle/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

![tingle](https://raw.githubusercontent.com/darthjee/tingle/master/tingle.png)

**Current Version:** [0.0.2](https://github.com/darthjee/tingle/releases/tag/0.0.2)
**Next Release:** [0.0.3](https://github.com/darthjee/tingle/compare/0.0.2...main)

Scripts in **shell**, **Python** and **Node.js** for simple, recurring tasks:
file scraping, bulk renaming, copying files between git branches,
and whatever else comes up in daily work.

## Installation

Install `tingle` without cloning the repo:

```
curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
```

This downloads the pinned release zip from GitHub Releases, unpacks it to
`~/.tingle`, and finishes by running `tingle install` (see [Commands](#commands)
below) to wire `tingle` into `~/.bashrc`.

Override defaults with one-off env var prefixes (not `export`):

```
TINGLE_VERSION=0.1.0 curl -fsSL https://raw.githubusercontent.com/darthjee/tingle/main/install/bootstrap.sh | bash
```

- `TINGLE_VERSION` — release tag to install, as plain `X.Y.Z` with no `v`
  prefix (default: the pinned version in `install/bootstrap.sh`).
- `TINGLE_REPO` — GitHub `owner/repo` to install from, e.g. your own fork
  (default: `darthjee/tingle`).
- `TINGLE_ASSUME_YES` — set to any value to skip the `y/N` confirmation
  prompt.

Prerequisites: `curl`, `unzip`, `bash`; `jq` for `bin/tingle`; `docker` for
`tingle linux`.

The installer places everything under `~/.tingle`. Once it finishes, run
`source ~/.bashrc` (or start a new shell) to pick up the `PATH` and
completion changes.

## Name Origin

The name **Tingle** is a tribute to the eccentric and iconic character from the
*The Legend of Zelda* series (reference: [Zelda Wiki](https://zelda.fandom.com/wiki/Tingle)).

In the game universe, Tingle is a "fairy" cartographer who lives to provide maps, items
and utilities to the hero — always in a peculiar, fun and unusual way. He exists
to offer the right tool at the right time.

By analogy, **Tingle** is the repository where I keep the small utilities
I use in my daily work: each script is a small but essential tool,
ready to solve the task of the moment — with no single theme, but each one doing
its part. Like Tingle, the project is light, versatile and a bit peculiar.

## Structure

```
tingle/
├── bin/            # Callable entry points (on PATH), calling into shell/python/node
├── commands/       # Per-language command mappings (commands/<lang>.json) loaded by bin/tingle
├── completions/    # Bash completion script for tingle
├── shell/          # Bash/Shell scripts
├── python/         # Python scripts
├── node/           # Node.js scripts
└── README.md
```

## Scripts

| Script | Language | Description |
| --- | --- | --- |
| `check_file_size` | Python | Token efficiency triage: lists source files by line count against configurable warn/error/critical thresholds. |
| `kube` | Python | Kubernetes (EKS) helper with a scoped alias layer for switching contexts, listing namespaces/pods, and shelling into pods. |
| `tingle` | Shell | CLI hub — dispatches `tingle <command> [args...]` to the matching script under `python/`, `node/`, or `shell/` via `commands/*.json` mappings. |
| `install` | Shell | Adds `tingle` to `PATH` and installs bash completion, by idempotently appending a marker block to `~/.bashrc`. |
| `linux` | Shell | Runs real GNU/Linux command-line tools (`shell`, `sed`) inside a Docker container, mounting the current working directory in at the same path. |

## Commands

`bin/tingle` resolves the command name given as its first argument against
the mappings defined in `commands/*.json` (one file per language, loaded in
alphabetical order — `node.json`, `python.json`, `shell.json`) and executes
the matching script. Each entry maps a command name to `{"path",
"short_help", "long_help"}`; on a name collision across files, the first
file that defines the name wins. These `commands/*.json` files are inert
JSON data, not sourced/executed code, and are read via `jq` (a required
dependency for `bin/tingle`).

Run `tingle`, `tingle help`, or `tingle --help` with no further arguments to
list all available commands with their short descriptions. Run `tingle
--help <command>` to see a command's full description. An unknown command
prints an error along with the same command listing, and exits non-zero.

Run `tingle install` to wire up `tingle` for interactive shell use: it
idempotently appends a marker block to `~/.bashrc` that adds `tingle` to
`PATH` and sources `completions/tingle.bash`, enabling `tingle <TAB>` bash
completion of command names. This is the same shell-wiring step the
[web installer](#installation) finishes with, so re-running it by hand is
only needed if you skip the one-liner and set up an already-cloned repo
manually.

## Usage

Each script is independent and can be run directly. Check each script's header
for usage instructions and dependencies.

## License

[MIT 2026](LICENSE)
