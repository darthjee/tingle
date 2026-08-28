#!/usr/bin/env python3
"""
executor.py — Orchestrator for the kube command.

Kubernetes (EKS) helper built around short, scoped aliases for contexts,
namespaces, and pods, backed by ~/.tingle/kube/config.json.

Usage:
    tingle kube switch <context_alias>
    tingle kube list namespace
    tingle kube list pods
    tingle kube shell <namespace_alias> <pod_alias>
    tingle kube configure context
    tingle kube configure namespace
    tingle kube configure pod
"""

from __future__ import annotations


class Kube:
    """Orchestrate the kube subcommands: switch, list, shell, configure."""

    def run(self, args: list[str]):
        """Entry point for the script."""
