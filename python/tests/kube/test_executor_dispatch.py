"""Unit tests for kube.executor.Kube._configure dispatch and Kube.run."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.executor import Kube


@patch("kube.executor.configure_pod")
@patch("kube.executor.configure_namespace")
@patch("kube.executor.configure_context")
@patch("kube.executor.KubeConfig")
def test_configure_dispatches_to_configure_context(
    mock_config_cls, mock_configure_context, mock_configure_namespace, mock_configure_pod
):
    mock_config = MagicMock()
    mock_config_cls.return_value = mock_config

    Kube._configure({"configure_target": "context"})

    mock_configure_context.assert_called_once_with(mock_config)
    mock_configure_namespace.assert_not_called()
    mock_configure_pod.assert_not_called()


@patch("kube.executor.configure_pod")
@patch("kube.executor.configure_namespace")
@patch("kube.executor.configure_context")
@patch("kube.executor.KubeConfig")
def test_configure_dispatches_to_configure_namespace(
    mock_config_cls, mock_configure_context, mock_configure_namespace, mock_configure_pod
):
    mock_config = MagicMock()
    mock_config_cls.return_value = mock_config

    Kube._configure({"configure_target": "namespace"})

    mock_configure_namespace.assert_called_once_with(mock_config)
    mock_configure_context.assert_not_called()
    mock_configure_pod.assert_not_called()


@patch("kube.executor.configure_pod")
@patch("kube.executor.configure_namespace")
@patch("kube.executor.configure_context")
@patch("kube.executor.KubeConfig")
def test_configure_dispatches_to_configure_pod(
    mock_config_cls, mock_configure_context, mock_configure_namespace, mock_configure_pod
):
    mock_config = MagicMock()
    mock_config_cls.return_value = mock_config

    Kube._configure({"configure_target": "pod"})

    mock_configure_pod.assert_called_once_with(mock_config)
    mock_configure_context.assert_not_called()
    mock_configure_namespace.assert_not_called()


@patch("kube.executor.configure_context")
@patch("kube.executor.KubeConfig")
def test_run_prints_notice_when_set_without_pass_through(
    mock_config_cls, mock_configure_context, capsys
):
    mock_config = MagicMock()
    mock_config.pass_through = False
    mock_config.notice = "kube: created new config at /some/path"
    mock_config_cls.return_value = mock_config

    Kube().run(["configure", "context"])

    out = capsys.readouterr().out
    assert "kube: created new config at /some/path" in out
