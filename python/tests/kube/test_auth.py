"""Unit tests for kube.auth: credential-source detection and the AWS pre-check."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.auth import check_aws_credentials, detect_credential_source


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


@patch("kube.auth.binaries.resolve", side_effect=lambda name: name)
@patch("kube.auth.subprocess.run")
def test_passes_correct_profile_through(mock_run, mock_resolve):
    mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")

    check_aws_credentials("qa-profile")

    mock_run.assert_called_once_with(
        ["aws", "sts", "get-caller-identity", "--profile", "qa-profile"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("kube.auth.binaries.resolve", side_effect=lambda name: name)
@patch("kube.auth.subprocess.run")
def test_none_profile_omits_profile_flag(mock_run, mock_resolve):
    mock_run.return_value = MagicMock(returncode=0, stdout="{}", stderr="")

    check_aws_credentials(None)

    mock_run.assert_called_once_with(
        ["aws", "sts", "get-caller-identity"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_detect_env_with_session_token(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAEXAMPLE")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "token")

    assert detect_credential_source() == "env"


def test_detect_env_without_session_token(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAEXAMPLE")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.delenv("AWS_SESSION_TOKEN", raising=False)

    assert detect_credential_source() == "env"


def test_detect_partial_with_only_access_key(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAEXAMPLE")
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

    assert detect_credential_source() == "partial"


def test_detect_partial_with_only_secret(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")

    assert detect_credential_source() == "partial"


def test_detect_empty_string_counts_as_unset(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIAEXAMPLE")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "  ")

    assert detect_credential_source() == "partial"


def test_detect_profile_when_neither_set(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.setenv("AWS_SESSION_TOKEN", "token")

    assert detect_credential_source() == "profile"


def test_detect_both_empty_strings_count_as_profile(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "")

    assert detect_credential_source() == "profile"
