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


def _pod(name, timestamp):
    return {"metadata": {"name": name, "creationTimestamp": timestamp}}


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
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_aborts_when_aws_precheck_fails(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (False, "Unable to locate credentials")
    config = _config(aws_profile="prod")

    Kube._list_pods({"list_target": "pods", "namespace": "default"}, config)

    mock_check.assert_called_once_with("prod")
    mock_list_pods.assert_not_called()
    out = capsys.readouterr().out
    assert "AWS credential check failed" in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_prints_namespace_alias_notice_on_pass_through(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = ([], None)
    config = _config(namespaces={"prod": {"default": "prod-default-ns"}})

    Kube._list_pods({"list_target": "pods", "namespace": "unknown"}, config)

    mock_list_pods.assert_called_once_with("unknown")
    out = capsys.readouterr().out
    assert "not found in configured namespaces" in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_prints_inventory_error_on_nonexistent_namespace(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = ([], 'namespaces "nonexistent" not found')
    config = _config(namespaces={"prod": {"default": "prod-default-ns"}})

    Kube._list_pods({"list_target": "pods", "namespace": "default"}, config)

    out = capsys.readouterr().out
    assert 'namespaces "nonexistent" not found' in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_groups_matched_pods_per_alias_in_deterministic_order(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [
            _pod("my-pod-bbbbbbbbbb", "2024-01-02T00:00:00Z"),
            _pod("my-pod-aaaaaaaaaa", "2024-01-01T00:00:00Z"),
            _pod("my-pod-super-cccccccccc", "2024-01-01T00:00:00Z"),
        ],
        None,
    )
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._list_pods({"list_target": "pods", "namespace": "default"}, config)

    out = capsys.readouterr().out
    assert "api:" in out
    assert "my-pod-aaaaaaaaaa" in out
    assert "my-pod-bbbbbbbbbb" in out
    assert "my-pod-super-cccccccccc" not in out
    assert out.index("my-pod-aaaaaaaaaa") < out.index("my-pod-bbbbbbbbbb")
