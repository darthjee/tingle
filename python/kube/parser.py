"""
parser.py — Subcommand-aware argument parser for kube.

`switch`, `list`, `shell`, and `configure` each take a different argument
shape, so this wraps `argparse.ArgumentParser` with `add_subparsers()`
directly rather than the flat flag-list `python/common/arg_parser.py`
supports (which stays scoped to `check_file_size`).

Usage:
    tingle kube switch <context_alias>
    tingle kube list namespace
    tingle kube list pods --namespace <alias>
    tingle kube shell <namespace_alias> <pod_alias>
    tingle kube configure context|namespace|pod
"""

from __future__ import annotations

import argparse


class KubeArgParser:
    """Build and parse kube's subcommand-shaped command-line arguments."""

    def parse(self, argv: list[str] | None = None) -> dict:
        """Parse argv (defaulting to sys.argv[1:]) and return a dict."""
        namespace = self.build().parse_args(argv)
        return vars(namespace)

    def build(self) -> argparse.ArgumentParser:
        """Build and return the configured argument parser."""
        parser = argparse.ArgumentParser(prog="kube")
        subparsers = parser.add_subparsers(dest="subcommand", required=True)

        self._build_switch(subparsers)
        self._build_list(subparsers)
        self._build_shell(subparsers)
        self._build_configure(subparsers)

        return parser

    @staticmethod
    def _build_switch(subparsers) -> None:
        switch_parser = subparsers.add_parser("switch", help="Switch the active context")
        switch_parser.add_argument("context_alias", help="Alias of the context to switch to")

    @staticmethod
    def _build_list(subparsers) -> None:
        list_parser = subparsers.add_parser("list", help="List namespaces or pods")
        list_subparsers = list_parser.add_subparsers(dest="list_target", required=True)

        list_subparsers.add_parser("namespace", help="List configured namespace aliases")

        pods_parser = list_subparsers.add_parser("pods", help="List configured pod aliases")
        pods_parser.add_argument(
            "--namespace",
            required=True,
            help="Namespace alias to scope the pod list to",
        )

    @staticmethod
    def _build_shell(subparsers) -> None:
        shell_parser = subparsers.add_parser("shell", help="Open a shell into a pod")
        shell_parser.add_argument("namespace_alias", help="Alias of the target namespace")
        shell_parser.add_argument("pod_alias", help="Alias of the target pod")

    @staticmethod
    def _build_configure(subparsers) -> None:
        configure_parser = subparsers.add_parser("configure", help="Configure kube aliases")
        configure_subparsers = configure_parser.add_subparsers(
            dest="configure_target", required=True
        )

        configure_subparsers.add_parser("context", help="Configure a context alias")
        configure_subparsers.add_parser("namespace", help="Configure a namespace alias")
        configure_subparsers.add_parser("pod", help="Configure a pod alias")
