# Plan: Configuration: interactive configure + polish

Issue: [24-configuration-interactive-configure-polish.md](../issues/24-configuration-interactive-configure-polish.md)

## Overview

Implement `tingle kube configure context|namespace|pod` as a prompt-only interactive flow that creates/edits/removes aliases in `~/.tingle/kube/config.json`, validating the resulting structure before every save so a bad session never corrupts the file on disk. Alongside that, close out the remaining polish from the parent spec: `--json` output on `list namespace`/`list pods`, and a sweep of Section 6's edge-case error messages across `switch`/`list`/`shell`. All logic lives in `python/kube/`; `cli` only updates the command's registered help text to document the new `--json` flag and `configure` behavior.

## Agents involved

- [python](python.md)
- [cli](cli.md)

## Shared contracts

- **CLI surface documented in `commands/python.json`**: `python` owns the actual `argparse` flags (a new `--json` flag on `kube list`, unchanged `configure context|namespace|pod` subcommands already registered in `parser.py`). `cli` owns keeping `commands/python.json`'s `kube` entry's `long_help`/examples in sync with that surface — specifically: mention `list namespace --json` / `list pods --json`, and that `configure context|namespace|pod` now supports interactive create/edit/remove instead of being a stub. No field names or payload shapes cross this boundary beyond that help text; `cli` does not touch `python/`.
