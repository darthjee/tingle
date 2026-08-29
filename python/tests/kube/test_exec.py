"""Unit tests for kube.exec."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.exec import exec_shell, prompt_pod_choice


@patch("kube.exec.subprocess.run")
def test_exec_shell_success_returns_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0)

    success, error = exec_shell("default", "api-abc1234567", "/bin/sh")

    assert success is True
    assert error is None
    mock_run.assert_called_once_with(
        ["kubectl", "exec", "-n", "default", "-it", "api-abc1234567", "--", "/bin/sh"],
        check=False,
    )


@patch("kube.exec.subprocess.run")
def test_exec_shell_does_not_capture_output(mock_run):
    mock_run.return_value = MagicMock(returncode=0)

    exec_shell("default", "api-abc1234567", "/bin/sh")

    _, kwargs = mock_run.call_args
    assert "capture_output" not in kwargs
    assert "text" not in kwargs
    assert "stdout" not in kwargs
    assert "stderr" not in kwargs


@patch("kube.exec.subprocess.run")
def test_exec_shell_nonzero_exit_returns_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1)

    success, error = exec_shell("default", "api-abc1234567", "/bin/sh")

    assert success is False
    assert error is not None


def test_prompt_pod_choice_valid_selection_returns_pod():
    candidates = [
        {"metadata": {"name": "api-abc1234567"}},
        {"metadata": {"name": "api-def1234567"}},
    ]

    with patch("builtins.input", return_value="2"):
        chosen = prompt_pod_choice(candidates)

    assert chosen == candidates[1]


def test_prompt_pod_choice_invalid_then_valid_input_reprompts():
    candidates = [
        {"metadata": {"name": "api-abc1234567"}},
        {"metadata": {"name": "api-def1234567"}},
    ]

    with patch("builtins.input", side_effect=["not-a-number", "9", "1"]):
        chosen = prompt_pod_choice(candidates)

    assert chosen == candidates[0]


def test_prompt_pod_choice_empty_input_returns_none():
    candidates = [{"metadata": {"name": "api-abc1234567"}}]

    with patch("builtins.input", return_value=""):
        chosen = prompt_pod_choice(candidates)

    assert chosen is None
