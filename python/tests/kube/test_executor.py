"""Unit tests for kube.executor.Kube._switch."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.executor import Kube


def _config(contexts=None, aws_profile="default"):
    config = MagicMock()
    config.data = {"contexts": contexts or {}, "aws_profile": aws_profile}
    return config


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
def test_switch_with_resolved_alias_succeeds(mock_check, mock_switch, mock_list, capsys):
    mock_check.return_value = (True, None)
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"})

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with("default")
    mock_switch.assert_called_once_with("arn:aws:eks:prod")
    mock_list.assert_not_called()
    out = capsys.readouterr().out
    assert "prod" in out
    assert "arn:aws:eks:prod" in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
def test_switch_with_unresolved_alias_prints_notice_and_passes_through(
    mock_check, mock_switch, mock_list, capsys
):
    mock_check.return_value = (True, None)
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"})

    Kube._switch({"context_alias": "unknown-context"}, config)

    mock_switch.assert_called_once_with("unknown-context")
    out = capsys.readouterr().out
    assert "not found in configured contexts" in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
def test_switch_aborts_when_aws_precheck_fails(mock_check, mock_switch, mock_list, capsys):
    mock_check.return_value = (False, "Unable to locate credentials")
    config = _config(contexts={"prod": "arn:aws:eks:prod"}, aws_profile="prod")

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with("prod")
    mock_switch.assert_not_called()
    mock_list.assert_not_called()
    out = capsys.readouterr().out
    assert "AWS credential check failed" in out
    assert "Unable to locate credentials" in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
def test_switch_prints_suggestions_on_nonexistent_context(
    mock_check, mock_switch, mock_list, capsys
):
    mock_check.return_value = (True, None)
    mock_switch.return_value = (False, "no context exists")
    mock_list.return_value = ["prod", "qa"]
    config = _config(contexts={"prod": "arn:aws:eks:prod", "qa": "arn:aws:eks:qa"})

    Kube._switch({"context_alias": "unknown"}, config)

    mock_list.assert_called_once_with(config.data["contexts"])
    out = capsys.readouterr().out
    assert "failed to switch" in out
    assert "prod" in out
    assert "qa" in out
