# Plan: Foundation: command skeleton + config layer

Issue: [20-foundation-command-skeleton-config-layer.md](../issues/20-foundation-command-skeleton-config-layer.md)

## Overview

Introduce `tingle kube` as a new Python-backed subcommand: register it in the dispatcher's command mapping, scaffold a `python/kube/` package with its own subcommand-aware argument parser (`switch`/`list`/`shell`/`configure`, stub behavior only), and implement a config-reading layer for `~/.tingle/kube/config.json` (schema validation, defaults, pass-through on missing/invalid config), backed by unit tests. This is the first of five serial `tingle kube` child issues (#20-#24); no cluster/AWS interaction happens yet.

## Agents involved

- [python](python.md)
- [cli](cli.md)

## Shared contracts

- **Command registration entry** — `cli` adds a `"kube"` key to `commands/python.json` shaped like the existing `"check_file_size"` entry:
  ```json
  {
    "kube": {
      "path": "python/kube/main.py",
      "short_help": "...",
      "long_help": "..."
    }
  }
  ```
  `path` must point at the file `python` creates (`python/kube/main.py`). `python` owns the file's existence and behavior; `cli` owns the registration entry and its `short_help`/`long_help` text.
- **Invocation convention** — `bin/tingle kube <args...>` resolves to `python/kube/main.py run <args...>` (the dispatcher always prepends the `run` flow verb). `python/kube/main.py` must accept `run` as `argv[1]` and forward `argv[2:]` to the orchestrator, exactly like `python/check_file_size/main.py` does — this is what makes the registration in `commands/python.json` actually work end-to-end.
