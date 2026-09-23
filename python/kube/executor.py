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

import json

from kube.auth import check_aws_credentials, detect_credential_source
from kube.config import KubeConfig
from kube.configure import configure_context, configure_namespace, configure_pod
from kube.constants import Constants
from kube.exec import exec_shell, prompt_pod_choice
from kube.inventory import get_pod, list_namespaces, list_pods
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

        if config.notice:
            print(config.notice)

        handler = self._handlers(config).get(parsed["subcommand"])
        if handler:
            handler(parsed)

    def _handlers(self, config: KubeConfig) -> dict:
        """Map each subcommand to its handler."""
        return {
            "switch": lambda parsed: self._switch(parsed, config),
            "list": lambda parsed: self._list(parsed, config),
            "shell": lambda parsed: self._shell(parsed, config),
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

        if not Kube._check_aws_credentials(config, "switch"):
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
    def _check_aws_credentials(config: KubeConfig, command: str) -> bool:
        """Run the AWS pre-check for `kube <command>`, printing an abort message on failure.

        Detects the credential source first: exported environment
        credentials are checked without `--profile` (printing a notice that
        `aws_profile` is ignored); incomplete environment credentials print a
        warning and fall back to the configured profile.
        """
        source = detect_credential_source()
        aws_profile = config.data.get("aws_profile", Constants.DEFAULT_AWS_PROFILE)

        if source == "env":
            print("kube: using AWS credentials from environment (aws_profile ignored)")
            credentials_ok, credentials_error = check_aws_credentials(None)
        else:
            if source == "partial":
                print(
                    "kube: warning: incomplete AWS environment credentials "
                    "(need both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY); "
                    f"falling back to profile '{aws_profile}'"
                )
            credentials_ok, credentials_error = check_aws_credentials(aws_profile)

        if not credentials_ok:
            target = (
                "environment credentials" if source == "env" else f"profile '{aws_profile}'"
            )
            print(
                f"kube {command}: AWS credential check failed for {target}: "
                f"{credentials_error}"
            )
        return credentials_ok

    @staticmethod
    def _match_pods_for_alias(items: list, alias_config: dict, default_id_pattern: str) -> tuple:
        """Match `items` against an alias's prefix/id_pattern.

        Returns `(matched, discarded)`, where `discarded` lists the names of
        `items` whose `metadata.name` starts with the alias's `prefix` but
        were not matched — computed only when nothing matched.
        """
        prefix = alias_config["prefix"]
        matched = match_pods(
            items,
            prefix,
            alias_config.get("id_pattern"),
            default_id_pattern,
        )

        discarded = []
        if not matched:
            discarded = [
                item["metadata"]["name"]
                for item in items
                if item["metadata"]["name"].startswith(prefix)
            ]

        return matched, discarded

    @staticmethod
    def _list_namespace(parsed: dict, config: KubeConfig) -> None:
        """Handle `kube list namespace`: list real namespaces, annotated with aliases."""
        if not Kube._check_aws_credentials(config, "list"):
            return

        active_scope = detect_active_scope(config.data.get("contexts", {}))

        items, error = list_namespaces()
        if error:
            print(error)
            return

        scoped_namespaces = config.data.get("namespaces", {}).get(active_scope, {})
        reverse = {real_name: alias for alias, real_name in scoped_namespaces.items()}

        if parsed.get("json"):
            payload = [
                {"alias": reverse.get(item["metadata"]["name"]), "name": item["metadata"]["name"]}
                for item in items
            ]
            print(json.dumps(payload, indent=2))
            return

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
        if not Kube._check_aws_credentials(config, "list"):
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
        scoped_pods = active_scope_pods(config.data.get("pods", {}), active_scope)
        pods = {
            alias: alias_config
            for alias, alias_config in scoped_pods.items()
            if alias_config.get("namespace") in (None, parsed["namespace"])
        }

        if parsed.get("json"):
            payload = Kube._pods_json_payload(pods, items, default_id_pattern)
            print(json.dumps(payload, indent=2))
            return

        Kube._print_pods_text(pods, items, default_id_pattern)

    @staticmethod
    def _pods_json_payload(pods: dict, items: list, default_id_pattern: str) -> list:
        """Build the `kube list pods --json` payload for each alias."""
        payload = []
        for alias, alias_config in pods.items():
            matched, _discarded = Kube._match_pods_for_alias(
                items, alias_config, default_id_pattern
            )
            payload.append(
                {
                    "alias": alias,
                    "pods": [pod["metadata"]["name"] for pod in matched],
                }
            )
        return payload

    @staticmethod
    def _print_pods_text(pods: dict, items: list, default_id_pattern: str) -> None:
        """Print the `kube list pods` text output for each alias."""
        for alias, alias_config in pods.items():
            matched, discarded = Kube._match_pods_for_alias(
                items, alias_config, default_id_pattern
            )
            print(f"{alias}:")
            for pod in matched:
                print(f"  - {pod['metadata']['name']}")

            if not matched and discarded:
                print(f"  kube list: candidates discarded by id_pattern for '{alias}':")
                for name in discarded:
                    print(f"    - {name}")

    @staticmethod
    def _resolve_real_pod(
        parsed: dict, real_namespace: str, active_scope: str, config: KubeConfig
    ) -> str | None:
        """Resolve `parsed['pod_alias']` to a real pod name in `real_namespace`.

        Returns the real pod name on success, or `None` when resolution
        failed — in every `None` case this method has already printed the
        reason.
        """
        pod_alias = parsed["pod_alias"]
        scoped_pods = active_scope_pods(config.data.get("pods", {}), active_scope)

        if pod_alias not in scoped_pods:
            notice = (
                f"kube: '{pod_alias}' not found in configured pods — using it as-is."
            )
            print(notice)
            return pod_alias

        alias_config = scoped_pods[pod_alias]
        pod_namespace = alias_config.get("namespace")
        if pod_namespace and pod_namespace != parsed["namespace_alias"]:
            print(
                f"kube shell: warning — pod alias '{pod_alias}' is configured for "
                f"namespace '{pod_namespace}', not '{parsed['namespace_alias']}' — "
                f"proceeding with '{parsed['namespace_alias']}'"
            )

        default_id_pattern = config.data.get(
            "pod_id_pattern", Constants.DEFAULT_POD_ID_PATTERN
        )

        items, error = list_pods(real_namespace)
        if error:
            print(error)
            return None

        matched, discarded = Kube._match_pods_for_alias(
            items, alias_config, default_id_pattern
        )

        if not matched:
            print(f"kube shell: no pods matched alias '{pod_alias}' in '{real_namespace}'")
            if discarded:
                print("kube shell: candidates discarded by id_pattern:")
                for name in discarded:
                    print(f"  - {name}")
            return None

        if len(matched) == 1:
            return matched[0]["metadata"]["name"]

        chosen = prompt_pod_choice(matched)
        if chosen is None:
            print("kube shell: no pod selected")
            return None
        return chosen["metadata"]["name"]

    @staticmethod
    def _shell(parsed: dict, config: KubeConfig) -> None:
        """Handle `kube shell <namespace_alias> <pod_alias>`: resolve, pre-check, exec."""
        if not Kube._check_aws_credentials(config, "shell"):
            return

        active_scope = detect_active_scope(config.data.get("contexts", {}))

        namespaces = config.data.get("namespaces", {})
        real_namespace, namespace_notice = resolve_namespace_alias(
            namespaces, active_scope, parsed["namespace_alias"]
        )
        if namespace_notice:
            print(namespace_notice)

        real_pod = Kube._resolve_real_pod(parsed, real_namespace, active_scope, config)
        if real_pod is None:
            return

        pod, error = get_pod(real_namespace, real_pod)
        if error:
            print(error)
            return

        if pod.get("status", {}).get("phase") != "Running":
            print(f"kube shell: warning — pod '{real_pod}' is not in Running phase")

        shell = config.data.get("shell", Constants.DEFAULT_SHELL)
        success, exec_error = exec_shell(real_namespace, real_pod, shell)
        if not success:
            print(exec_error)

    @staticmethod
    def _configure(parsed: dict) -> None:
        """Handle `kube configure context|namespace|pod`: dispatch to `configure.py`.

        Loads its own fresh `KubeConfig()` rather than the one loaded for
        read-only commands in `run()`, since `configure` edits `config.raw`
        (the pre-default dict), not `config.data`.
        """
        config = KubeConfig()
        {
            "context": configure_context,
            "namespace": configure_namespace,
            "pod": configure_pod,
        }[parsed["configure_target"]](config)
