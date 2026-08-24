# Plan: Add tingle hub

Issue: [3-add-tingle-hub.md](../../issues/3-add-tingle-hub.md)

## Overview

Add a `bin/tingle` CLI hub that dispatches commands to scripts under `python/`, `node/`, or `shell/` via per-language mapping files sourced from a new root-level `commands/` directory, and relocate the existing `bin/check_file_size.py` to `python/check_file_size.py` as the first mapped command.

## Agents involved

- [cli](cli.md)
- [python](python.md)

## Shared contracts

- **Command name**: `check_file_size`
- **Script path** (relative to `TINGLE_FOLDER`, as referenced by `commands/python.sh`): `python/check_file_size.py`
- The `python` agent must ensure the relocated script keeps its shebang (`#!/usr/bin/env python3`), its executable bit (`chmod +x`), and its existing CLI contract unchanged — positional `path` argument plus `--warn`/`--error`/`--critical`/`--top`/`--exclude`/`--ext` — since `bin/tingle` invokes it directly via `"$path" "$@"` with no interpreter wrapping.
- The `cli` agent's `commands/python.sh` must map `check_file_size="python/check_file_size.py"`, matching that exact path.
