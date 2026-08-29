#!/usr/bin/env python3
"""
executor.py — Orchestrator for the kube command.

Kubernetes (EKS) helper built around short, scoped aliases for contexts,
namespaces, and pods, backed by ~/.tingle/kube/config.json.

Usage:
    tingle kube switch <context_alias>
    tingle kube list namespace
    tingle kube list pods --namespace <alias>
    tingle kube shell <namespace_alias> <pod_alias>
    tingle kube configure context
    tingle kube configure namespace
    tingle kube configure pod
"""

from __future__ import annotations

from kube.auth import check_aws_credentials
from kube.config import KubeConfig
from kube.constants import Constants
from kube.inventory import list_namespaces, list_pods
from kube.matching import match_pods
from kube.parser import KubeArgParser
from kube.scope import (
    active_scope_pods,
    detect_active_scope,
    list_available_contexts,
    resolve_context_alias,
    resolve_namespace_alias,
    switch_context,
)


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
            "list": lambda parsed: self._list(parsed, config),
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
    def _list(parsed: dict, config: KubeConfig) -> None:
        """Dispatch `kube list namespace|pods` to its handler."""
        if parsed["list_target"] == "namespace":
            Kube._list_namespace(parsed, config)
        elif parsed["list_target"] == "pods":
            Kube._list_pods(parsed, config)

    @staticmethod
    def _check_aws_credentials(config: KubeConfig) -> bool:
        """Run the AWS pre-check, printing an abort message on failure."""
        aws_profile = config.data.get("aws_profile", Constants.DEFAULT_AWS_PROFILE)
        credentials_ok, credentials_error = check_aws_credentials(aws_profile)
        if not credentials_ok:
            print(
                f"kube list: AWS credential check failed for profile "
                f"'{aws_profile}': {credentials_error}"
            )
        return credentials_ok

    @staticmethod
    def _list_namespace(parsed: dict, config: KubeConfig) -> None:
        """Handle `kube list namespace`: list real namespaces, annotated with aliases."""
        if not Kube._check_aws_credentials(config):
            return

        active_scope = detect_active_scope(config.data.get("contexts", {}))

        items, error = list_namespaces()
        if error:
            print(error)
            return

        scoped_namespaces = config.data.get("namespaces", {}).get(active_scope, {})
        reverse = {real_name: alias for alias, real_name in scoped_namespaces.items()}

        for item in items:
            name = item["metadata"]["name"]
            alias = reverse.get(name)
            if alias:
                print(f"{alias} -> {name}")
            else:
                print(name)

    @staticmethod
    def _list_pods(parsed: dict, config: KubeConfig) -> None:
        """Handle `kube list pods --namespace <alias>`: list matched pods per alias."""
        if not Kube._check_aws_credentials(config):
            return

        active_scope = detect_active_scope(config.data.get("contexts", {}))

        namespaces = config.data.get("namespaces", {})
        real_namespace, notice = resolve_namespace_alias(
            namespaces, active_scope, parsed["namespace"]
        )
        if notice:
            print(notice)

        items, error = list_pods(real_namespace)
        if error:
            print(error)
            return

        default_id_pattern = config.data.get("pod_id_pattern", Constants.DEFAULT_POD_ID_PATTERN)
        pods = active_scope_pods(config.data.get("pods", {}), active_scope)

        for alias, alias_config in pods.items():
            matched = match_pods(
                items,
                alias_config["prefix"],
                alias_config.get("id_pattern"),
                default_id_pattern,
            )
            print(f"{alias}:")
            for pod in matched:
                print(f"  - {pod['metadata']['name']}")

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
