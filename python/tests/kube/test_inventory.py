"""Unit tests for kube.inventory."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.inventory import get_pod, list_namespaces, list_pods


@patch("kube.inventory.subprocess.run")
def test_list_namespaces_success_returns_items(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"items": [{"metadata": {"name": "default"}}]}',
        stderr="",
    )

    items, error = list_namespaces()

    assert items == [{"metadata": {"name": "default"}}]
    assert error is None
    mock_run.assert_called_once_with(
        ["kubectl", "get", "namespaces", "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("kube.inventory.subprocess.run")
def test_list_namespaces_kubectl_failure_returns_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="kubectl error")

    items, error = list_namespaces()

    assert items == []
    assert error == "kubectl error"


@patch("kube.inventory.subprocess.run")
def test_list_namespaces_invalid_json_returns_error(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="not-json", stderr="")

    items, error = list_namespaces()

    assert items == []
    assert error is not None


@patch("kube.inventory.subprocess.run")
def test_list_pods_success_returns_items(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"items": [{"metadata": {"name": "api-abc1234567"}}]}',
        stderr="",
    )

    items, error = list_pods("default")

    assert items == [{"metadata": {"name": "api-abc1234567"}}]
    assert error is None
    mock_run.assert_called_once_with(
        ["kubectl", "get", "pods", "-n", "default", "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("kube.inventory.subprocess.run")
def test_list_pods_nonexistent_namespace_returns_error(mock_run):
    mock_run.return_value = MagicMock(
        returncode=1, stdout="", stderr='namespaces "nonexistent" not found'
    )

    items, error = list_pods("nonexistent")

    assert items == []
    assert error == 'namespaces "nonexistent" not found'


@patch("kube.inventory.subprocess.run")
def test_list_pods_invalid_json_returns_error(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="not-json", stderr="")

    items, error = list_pods("default")

    assert items == []
    assert error is not None


@patch("kube.inventory.subprocess.run")
def test_get_pod_success_returns_pod(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"metadata": {"name": "api-abc1234567"}}',
        stderr="",
    )

    pod, error = get_pod("default", "api-abc1234567")

    assert pod == {"metadata": {"name": "api-abc1234567"}}
    assert error is None
    mock_run.assert_called_once_with(
        ["kubectl", "get", "pod", "-n", "default", "api-abc1234567", "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("kube.inventory.subprocess.run")
def test_get_pod_nonexistent_pod_returns_error(mock_run):
    mock_run.return_value = MagicMock(
        returncode=1, stdout="", stderr='pods "nonexistent" not found'
    )

    pod, error = get_pod("default", "nonexistent")

    assert pod is None
    assert error == 'pods "nonexistent" not found'


@patch("kube.inventory.subprocess.run")
def test_get_pod_invalid_json_returns_error(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="not-json", stderr="")

    pod, error = get_pod("default", "api-abc1234567")

    assert pod is None
    assert error is not None
