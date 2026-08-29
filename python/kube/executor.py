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

from kube.auth import check_aws_credentials
from kube.config import KubeConfig
from kube.constants import Constants
from kube.parser import KubeArgParser
from kube.scope import list_available_contexts, resolve_context_alias, switch_context


class Kube:
    """Orchestrate the kube subcommands: switch, list, shell, configure."""

    def run(self, args: list[str]) -> None:
        """Entry point for the script."""
        parsed = KubeArgParser().parse(args)
        config = KubeConfig()

        if config.pass_through:
            print(config.notice)

        handler = self._handlers(config).get(parsed["subcommand"])
        if handler:
            handler(parsed)

    def _handlers(self, config: KubeConfig) -> dict:
        """Map each subcommand to its handler."""
        return {
            "switch": lambda parsed: self._switch(parsed, config),
            "list": self._list,
            "shell": self._shell,
            "configure": self._configure,
        }

    @staticmethod
    def _switch(parsed: dict, config: KubeConfig) -> None:
        """Handle `kube switch <context_alias>`: resolve, pre-check, switch, validate."""
        context_alias = parsed["context_alias"]
        contexts = config.data.get("contexts", {})

        real_name, notice = resolve_context_alias(contexts, context_alias)
        if notice:
            print(notice)

        aws_profile = config.data.get("aws_profile", Constants.DEFAULT_AWS_PROFILE)
        credentials_ok, credentials_error = check_aws_credentials(aws_profile)
        if not credentials_ok:
            print(
                f"kube switch: AWS credential check failed for profile "
                f"'{aws_profile}': {credentials_error}"
            )
            return

        success, error = switch_context(real_name)
        if success:
            print(f"kube switch: now using context '{context_alias}' ({real_name})")
            return

        print(f"kube switch: failed to switch to '{real_name}': {error}")
        available = list_available_contexts(contexts)
        if available:
            print("kube switch: available contexts:")
            for name in available:
                print(f"  - {name}")

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
