"""Unit tests for kube.scope."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.scope import (
    active_scope_pods,
    detect_active_scope,
    list_available_contexts,
    resolve_context_alias,
    resolve_namespace_alias,
    switch_context,
)


def test_resolve_context_alias_found_returns_real_name_with_no_notice():
    contexts = {"prod": "arn:aws:eks:prod"}

    real_name, notice = resolve_context_alias(contexts, "prod")

    assert real_name == "arn:aws:eks:prod"
    assert notice is None


def test_resolve_context_alias_not_found_passes_through_with_notice():
    contexts = {"prod": "arn:aws:eks:prod"}

    real_name, notice = resolve_context_alias(contexts, "unknown")

    assert real_name == "unknown"
    assert notice is not None
    assert "unknown" in notice


@patch("kube.scope.subprocess.run")
def test_switch_context_validated_returns_success(mock_run):
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="", stderr=""),
        MagicMock(returncode=0, stdout="arn:aws:eks:prod\n", stderr=""),
    ]

    success, error = switch_context("arn:aws:eks:prod")

    assert success is True
    assert error is None
    assert mock_run.call_args_list[0].args[0] == ["kubectx", "arn:aws:eks:prod"]
    assert mock_run.call_args_list[1].args[0] == ["kubectl", "config", "current-context"]


@patch("kube.scope.subprocess.run")
def test_switch_context_kubectx_failure_returns_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="no context exists")

    success, error = switch_context("unknown-context")

    assert success is False
    assert error == "no context exists"


@patch("kube.scope.subprocess.run")
def test_switch_context_mismatch_after_kubectx_returns_error(mock_run):
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="", stderr=""),
        MagicMock(returncode=0, stdout="some-other-context\n", stderr=""),
    ]

    success, error = switch_context("arn:aws:eks:prod")

    assert success is False
    assert "arn:aws:eks:prod" in error
    assert "some-other-context" in error


@patch("kube.scope.subprocess.run")
def test_switch_context_kubectl_current_context_failure_returns_error(mock_run):
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="", stderr=""),
        MagicMock(returncode=1, stdout="", stderr="kubectl error"),
    ]

    success, error = switch_context("arn:aws:eks:prod")

    assert success is False
    assert error == "kubectl error"


def test_list_available_contexts_from_config():
    contexts = {"prod": "arn:aws:eks:prod", "qa": "arn:aws:eks:qa"}

    assert list_available_contexts(contexts) == ["prod", "qa"]


@patch("kube.scope.subprocess.run")
def test_list_available_contexts_falls_back_to_kubectl(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="arn:aws:eks:prod\narn:aws:eks:qa\n", stderr=""
    )

    result = list_available_contexts({})

    assert result == ["arn:aws:eks:prod", "arn:aws:eks:qa"]
    mock_run.assert_called_once_with(
        ["kubectl", "config", "get-contexts", "-o", "name"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("kube.scope.subprocess.run")
def test_list_available_contexts_kubectl_failure_returns_empty_list(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

    assert list_available_contexts({}) == []


@patch("kube.scope.subprocess.run")
def test_detect_active_scope_matches_alias(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="arn:aws:eks:prod\n", stderr="")
    contexts = {"prod": "arn:aws:eks:prod"}

    assert detect_active_scope(contexts) == "prod"


@patch("kube.scope.subprocess.run")
def test_detect_active_scope_no_match_returns_none(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="unlisted-context\n", stderr="")
    contexts = {"prod": "arn:aws:eks:prod"}

    assert detect_active_scope(contexts) is None


@patch("kube.scope.subprocess.run")
def test_detect_active_scope_kubectl_failure_returns_none(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

    assert detect_active_scope({}) is None


def test_resolve_namespace_alias_found_returns_real_name_with_no_notice():
    namespaces = {"prod": {"default": "prod-default-ns"}}

    real_name, notice = resolve_namespace_alias(namespaces, "prod", "default")

    assert real_name == "prod-default-ns"
    assert notice is None


def test_resolve_namespace_alias_not_found_passes_through_with_notice():
    namespaces = {"prod": {"default": "prod-default-ns"}}

    real_name, notice = resolve_namespace_alias(namespaces, "prod", "unknown")

    assert real_name == "unknown"
    assert notice is not None
    assert "unknown" in notice


def test_resolve_namespace_alias_no_active_scope_passes_through_with_notice():
    namespaces = {"prod": {"default": "prod-default-ns"}}

    real_name, notice = resolve_namespace_alias(namespaces, None, "default")

    assert real_name == "default"
    assert notice is not None


def test_active_scope_pods_returns_configured_aliases():
    pods = {"prod": {"api": {"prefix": "api-", "id_pattern": "^[a-z0-9]{10}$"}}}

    assert active_scope_pods(pods, "prod") == {
        "api": {"prefix": "api-", "id_pattern": "^[a-z0-9]{10}$"}
    }


def test_active_scope_pods_no_active_scope_returns_empty_dict():
    pods = {"prod": {"api": {"prefix": "api-"}}}

    assert active_scope_pods(pods, None) == {}


def test_active_scope_pods_missing_scope_returns_empty_dict():
    assert active_scope_pods({}, "prod") == {}
