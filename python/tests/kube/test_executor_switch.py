"""Unit tests for kube.executor.Kube._switch."""

from __future__ import annotations

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
    assert (
        "kube switch: AWS credential check failed for profile 'prod': "
        "Unable to locate credentials"
    ) in out
    assert "environment" not in out


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


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_switch_env_mode_prints_notice_and_skips_profile(
    mock_source, mock_check, mock_switch, mock_list, capsys
):
    mock_source.return_value = "env"
    mock_check.return_value = (True, None)
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"}, aws_profile="prod")

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with(None)
    out = capsys.readouterr().out
    assert "kube: using AWS credentials from environment (aws_profile ignored)" in out
    assert "warning" not in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_switch_partial_mode_warns_and_falls_back_to_profile(
    mock_source, mock_check, mock_switch, mock_list, capsys
):
    mock_source.return_value = "partial"
    mock_check.return_value = (True, None)
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"}, aws_profile="prod")

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with("prod")
    out = capsys.readouterr().out
    assert (
        "kube: warning: incomplete AWS environment credentials "
        "(need both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY); "
        "falling back to profile 'prod'"
    ) in out
    assert "kube: using AWS credentials from environment (aws_profile ignored)" not in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_switch_profile_mode_prints_no_notice(
    mock_source, mock_check, mock_switch, mock_list, capsys
):
    mock_source.return_value = "profile"
    mock_check.return_value = (True, None)
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"}, aws_profile="prod")

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with("prod")
    out = capsys.readouterr().out
    assert "kube: using AWS credentials from environment (aws_profile ignored)" not in out
    assert "incomplete AWS environment credentials" not in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_switch_env_mode_failure_mentions_environment_credentials(
    mock_source, mock_check, mock_switch, mock_list, capsys
):
    mock_source.return_value = "env"
    mock_check.return_value = (False, "Unable to locate credentials")
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"}, aws_profile="prod")

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with(None)
    mock_switch.assert_not_called()
    out = capsys.readouterr().out
    assert (
        "kube switch: AWS credential check failed for environment credentials: "
        "Unable to locate credentials"
    ) in out


@patch("kube.executor.list_available_contexts")
@patch("kube.executor.switch_context")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_switch_partial_mode_failure_mentions_profile(
    mock_source, mock_check, mock_switch, mock_list, capsys
):
    mock_source.return_value = "partial"
    mock_check.return_value = (False, "Unable to locate credentials")
    mock_switch.return_value = (True, None)
    config = _config(contexts={"prod": "arn:aws:eks:prod"}, aws_profile="prod")

    Kube._switch({"context_alias": "prod"}, config)

    mock_check.assert_called_once_with("prod")
    mock_switch.assert_not_called()
    out = capsys.readouterr().out
    assert (
        "kube switch: AWS credential check failed for profile 'prod': "
        "Unable to locate credentials"
    ) in out
