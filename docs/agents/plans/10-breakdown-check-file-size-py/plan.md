# Plan: Breakdown check_file_size.py

Issue: [10-breakdown-check-file-size-py.md](../issues/10-breakdown-check-file-size-py.md)

## Overview

Break `python/check_file_size.py` up into a small package of single-responsibility
classes, extract a generic, reusable `ArgParser` into `python/common/`, and
document the resulting layout as the standard pattern future Tingle commands
follow once they outgrow a single file.

## Agents involved

- [python](python.md)
- [product-owner](product-owner.md)

## Shared contracts

- **`python/common/arg_parser.py`** exposes a class `ArgParser`:
  - `ArgParser(flags: list[dict])` — `flags` is a list of dicts, each shaped
    like `argparse.add_argument`'s kwargs plus a `"name"` key for the flag
    string, e.g. `{"name": "--warn", "type": int, "default": 300, "help": "..."}`.
  - `.parse(argv: list[str] | None = None) -> dict` — parses (defaulting to
    `sys.argv[1:]`) and returns a plain `dict` of option name → value (not an
    `argparse.Namespace`).
  - Command-specific parsers (e.g. `check_file_size`'s) build their flag list
    and call `ArgParser(flags).parse()` instead of building their own
    `argparse.ArgumentParser`.
- **Command package layout convention** (`python` delivers it for
  `check_file_size`, `product-owner` documents it generally):
  - `commands/<lang>.json` continues to register each command's entry-point
    `path`; `bin/tingle` stays the single hub/dispatcher — unchanged.
  - A command's entry-point script is a thin shell: parse args (via the
    shared `ArgParser` where applicable), instantiate the command's
    orchestrator class, call it, exit.
  - Multi-file commands live under `python/<command>/`, package-style
    (`__init__.py` + one file per class), with the orchestrator class named
    after the command (e.g. `CheckFileSize` in
    `python/check_file_size/check_file_size.py`).
  - Reusable/common code (like `ArgParser`) lives in `python/common/`.

`product-owner`'s documentation must describe exactly this layout/API shape —
no independent design decisions on its side.
