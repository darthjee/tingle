"""Unit tests for kube.executor.Kube._list_namespace."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from kube.executor import Kube


def _config(contexts=None, aws_profile="default", namespaces=None, pods=None, **extra):
    config = MagicMock()
    config.data = {
        "contexts": contexts or {},
        "aws_profile": aws_profile,
        "namespaces": namespaces or {},
        "pods": pods or {},
        **extra,
    }
    return config


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_namespaces")
@patch("kube.executor.check_aws_credentials")
def test_list_namespace_aborts_when_aws_precheck_fails(
    mock_check, mock_list_namespaces, mock_detect, capsys
):
    mock_check.return_value = (False, "Unable to locate credentials")
    config = _config(aws_profile="prod")

    Kube._list_namespace({"list_target": "namespace"}, config)

    mock_check.assert_called_once_with("prod")
    mock_list_namespaces.assert_not_called()
    out = capsys.readouterr().out
    assert "AWS credential check failed" in out
    assert "Unable to locate credentials" in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_namespaces")
@patch("kube.executor.check_aws_credentials")
def test_list_namespace_prints_alias_arrow_name_and_bare_name(
    mock_check, mock_list_namespaces, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_namespaces.return_value = (
        [
            {"metadata": {"name": "prod-default-ns"}},
            {"metadata": {"name": "unaliased-ns"}},
        ],
        None,
    )
    config = _config(namespaces={"prod": {"default": "prod-default-ns"}})

    Kube._list_namespace({"list_target": "namespace"}, config)

    out = capsys.readouterr().out
    assert "default -> prod-default-ns" in out
    assert "unaliased-ns" in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_namespaces")
@patch("kube.executor.check_aws_credentials")
def test_list_namespace_prints_inventory_error(
    mock_check, mock_list_namespaces, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = None
    mock_list_namespaces.return_value = ([], "kubectl error")
    config = _config()

    Kube._list_namespace({"list_target": "namespace"}, config)

    out = capsys.readouterr().out
    assert "kubectl error" in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_namespaces")
@patch("kube.executor.check_aws_credentials")
def test_list_namespace_json_output(mock_check, mock_list_namespaces, mock_detect, capsys):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_namespaces.return_value = (
        [
            {"metadata": {"name": "prod-default-ns"}},
            {"metadata": {"name": "unaliased-ns"}},
        ],
        None,
    )
    config = _config(namespaces={"prod": {"default": "prod-default-ns"}})

    Kube._list_namespace({"list_target": "namespace", "json": True}, config)

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert {"alias": "default", "name": "prod-default-ns"} in payload
    assert {"alias": None, "name": "unaliased-ns"} in payload
