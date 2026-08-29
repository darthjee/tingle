"""Unit tests for kube.parser.KubeArgParser."""

from __future__ import annotations

import argparse

import pytest

from kube.parser import KubeArgParser


def test_parse_switch_identifies_subcommand_and_context_alias():
    result = KubeArgParser().parse(["switch", "qa"])

    assert result == {"subcommand": "switch", "context_alias": "qa"}


def test_parse_list_namespace_identifies_subcommand_and_target():
    result = KubeArgParser().parse(["list", "namespace"])

    assert result == {"subcommand": "list", "list_target": "namespace"}


def test_parse_list_pods_without_namespace_flag_raises():
    with pytest.raises(SystemExit):
        KubeArgParser().parse(["list", "pods"])


def test_parse_list_pods_with_namespace_flag():
    result = KubeArgParser().parse(["list", "pods", "--namespace", "web"])

    assert result == {"subcommand": "list", "list_target": "pods", "namespace": "web"}


def test_parse_shell_identifies_subcommand_and_aliases():
    result = KubeArgParser().parse(["shell", "web", "api"])

    assert result == {
        "subcommand": "shell",
        "namespace_alias": "web",
        "pod_alias": "api",
    }


@pytest.mark.parametrize("target", ["context", "namespace", "pod"])
def test_parse_configure_identifies_subcommand_and_target(target):
    result = KubeArgParser().parse(["configure", target])

    assert result == {"subcommand": "configure", "configure_target": target}


def test_parse_raises_when_subcommand_missing():
    with pytest.raises(SystemExit):
        KubeArgParser().parse([])


def test_parse_raises_when_switch_missing_context_alias():
    with pytest.raises(SystemExit):
        KubeArgParser().parse(["switch"])


def test_build_returns_usable_argument_parser():
    parser = KubeArgParser().build()

    assert isinstance(parser, argparse.ArgumentParser)
    # Should not raise.
    parser.print_help()
