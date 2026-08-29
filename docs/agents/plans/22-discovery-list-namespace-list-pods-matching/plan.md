# Plan: Discovery: list namespace + list pods + matching

Issue: [22-discovery-list-namespace-list-pods-matching.md](../issues/22-discovery-list-namespace-list-pods-matching.md)

## Overview

Implement `tingle kube list namespace` and `tingle kube list pods --namespace=<alias>`, replacing the stub handlers in `python/kube/executor.py`, and build the reusable namespace/pod alias resolution and pod-matching pipeline (prefix filter → `id_pattern` → deterministic ordering) that child #4's `shell` will later call into.

See [python.md](python.md) for the full plan.
