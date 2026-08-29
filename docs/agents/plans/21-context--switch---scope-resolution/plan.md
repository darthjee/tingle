# Plan: Context: switch + scope resolution

Issue: [21-context--switch---scope-resolution.md](../issues/21-context--switch---scope-resolution.md)

## Overview

Implement `tingle kube switch <context_alias>` for real, replacing the current stub in `python/kube/executor.py`. Adds two reusable building blocks for later `tingle kube` children — an AWS credential pre-check and active-scope detection — plus the first slice of context-alias resolution.

See [python.md](python.md) for the full plan.
