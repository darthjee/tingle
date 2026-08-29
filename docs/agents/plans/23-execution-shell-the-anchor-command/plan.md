# Plan: Execution: shell (the anchor command)

Issue: [23-execution-shell-the-anchor-command.md](../../issues/23-execution-shell-the-anchor-command.md)

## Overview

Implement `tingle kube shell <namespace_alias> <pod_alias>`, replacing the stub `Kube._shell` handler with real logic: resolve both aliases (reusing #21/#22's scope/matching layers), pre-validate the pod phase, and exec interactively into the resolved pod.

See [python.md](python.md) for the full plan.
