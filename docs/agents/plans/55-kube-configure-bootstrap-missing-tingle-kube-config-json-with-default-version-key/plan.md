# Plan: kube configure: bootstrap missing ~/.tingle/kube/config.json with default version key

Issue: [55-kube-configure-bootstrap-missing-tingle-kube-config-json-with-default-version-key.md](../issues/55-kube-configure-bootstrap-missing-tingle-kube-config-json-with-default-version-key.md)

## Overview

`KubeConfig` currently treats a missing config file the same as a malformed one: it flags pass-through mode and leaves `raw = {}`, so `configure context/namespace/pod` can never save a first alias (`version` is required but never gets a default). This plan moves the fix into `KubeConfig` itself so a missing file is bootstrapped in place — the directory and file are created with `{"version": Constants.CURRENT_VERSION}`, a one-line creation notice is printed, and every kube command (not just `configure`) benefits.

See [python.md](python.md) for the full plan.
