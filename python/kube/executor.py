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

from kube.config import KubeConfig
from kube.parser import KubeArgParser


class Kube:
    """Orchestrate the kube subcommands: switch, list, shell, configure."""

    def run(self, args: list[str]) -> None:
        """Entry point for the script."""
        parsed = KubeArgParser().parse(args)
        config = KubeConfig()

        if config.pass_through:
            print(config.notice)

        handler = self._handlers().get(parsed["subcommand"])
        if handler:
            handler(parsed)

    def _handlers(self) -> dict:
        """Map each subcommand to its stub handler."""
        return {
            "switch": self._switch,
            "list": self._list,
            "shell": self._shell,
            "configure": self._configure,
        }

    @staticmethod
    def _switch(parsed: dict) -> None:
        """Stub handler for `kube switch <context_alias>` (real logic: issue #21)."""
        print(f"kube switch: not yet implemented (context_alias={parsed['context_alias']})")

    @staticmethod
    def _list(parsed: dict) -> None:
        """Stub handler for `kube list namespace|pods` (real logic: issue #22)."""
        print(f"kube list {parsed['list_target']}: not yet implemented")

    @staticmethod
    def _shell(parsed: dict) -> None:
        """Stub handler for `kube shell <namespace_alias> <pod_alias>` (real logic: issue #23)."""
        print(
            "kube shell: not yet implemented "
            f"(namespace_alias={parsed['namespace_alias']}, pod_alias={parsed['pod_alias']})"
        )

    @staticmethod
    def _configure(parsed: dict) -> None:
        """Stub handler for `kube configure context|namespace|pod` (real logic: issue #24)."""
        print(f"kube configure {parsed['configure_target']}: not yet implemented")
