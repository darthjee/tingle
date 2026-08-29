"""Unit tests for kube.auth.check_aws_credentials."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.auth import check_aws_credentials


@patch("kube.auth.subprocess.run")
def test_success_returns_true_with_no_error(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")

    success, error = check_aws_credentials("default")

    assert success is True
    assert error is None


@patch("kube.auth.subprocess.run")
def test_failure_returns_false_with_stderr_surfaced(mock_run):
    mock_run.return_value = MagicMock(
        returncode=1, stdout="", stderr="Unable to locate credentials"
    )

    success, error = check_aws_credentials("default")

    assert success is False
    assert error == "Unable to locate credentials"


@patch("kube.auth.subprocess.run")
def test_failure_with_empty_stderr_returns_generic_message(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

    success, error = check_aws_credentials("default")

    assert success is False
    assert error == "aws sts get-caller-identity failed"


@patch("kube.auth.subprocess.run")
def test_passes_correct_profile_through(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")

    check_aws_credentials("qa-profile")

    mock_run.assert_called_once_with(
        ["aws", "sts", "get-caller-identity", "--profile", "qa-profile"],
        capture_output=True,
        text=True,
        check=False,
    )
