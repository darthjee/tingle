# Plan: Add Tingle Kube Autocomplete

Issue: [32-add-tingle-kube-autocomplete.md](../issues/32-add-tingle-kube-autocomplete.md)

## Overview

Add `python/kube/completion.py`, the first real `completion.<ext>` handler for the repo's existing generic completion framework, and wire `python/kube/main.py`'s flow-verb dispatcher to forward the `complete` verb to it. It returns static subcommand/flag keywords plus dynamic alias candidates read from `~/.tingle/kube/config.json` via `KubeConfig`, scoped by `scope.detect_active_scope()`.

See [python.md](python.md) for the full plan.
