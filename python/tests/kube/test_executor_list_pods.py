"""Unit tests for kube.executor.Kube._list_pods."""

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


def _pod(name, timestamp):
    return {"metadata": {"name": name, "creationTimestamp": timestamp}}


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


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_filters_candidates_by_own_namespace_field(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [
            _pod("app-aaaaaaaaaa", "2024-01-01T00:00:00Z"),
            _pod("db-bbbbbbbbbb", "2024-01-01T00:00:00Z"),
        ],
        None,
    )
    config = _config(
        namespaces={"prod": {"app": "prod-app-ns", "db": "prod-db-ns"}},
        pods={
            "prod": {
                "app": {"prefix": "app-", "namespace": "app"},
                "db": {"prefix": "db-", "namespace": "db"},
            }
        },
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._list_pods({"list_target": "pods", "namespace": "app"}, config)

    mock_list_pods.assert_called_once_with("prod-app-ns")
    out = capsys.readouterr().out
    assert "app:" in out
    assert "db:" not in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_keeps_alias_without_namespace_field_regardless_of_request(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [
            _pod("app-aaaaaaaaaa", "2024-01-01T00:00:00Z"),
            _pod("shared-cccccccccc", "2024-01-01T00:00:00Z"),
        ],
        None,
    )
    config = _config(
        namespaces={"prod": {"app": "prod-app-ns", "db": "prod-db-ns"}},
        pods={
            "prod": {
                "app": {"prefix": "app-", "namespace": "app"},
                "shared": {"prefix": "shared-"},
            }
        },
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._list_pods({"list_target": "pods", "namespace": "app"}, config)

    out = capsys.readouterr().out
    assert "app:" in out
    assert "shared:" in out


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_json_output(mock_check, mock_list_pods, mock_detect, capsys):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [_pod("my-pod-aaaaaaaaaa", "2024-01-01T00:00:00Z")],
        None,
    )
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._list_pods({"list_target": "pods", "namespace": "default", "json": True}, config)

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload == [{"alias": "api", "pods": ["my-pod-aaaaaaaaaa"]}]


@patch("kube.executor.detect_active_scope")
@patch("kube.executor.list_pods")
@patch("kube.executor.check_aws_credentials")
def test_list_pods_prints_discarded_candidates_when_alias_matches_nothing(
    mock_check, mock_list_pods, mock_detect, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [_pod("my-pod-bad-suffix", "2024-01-01T00:00:00Z")],
        None,
    )
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._list_pods({"list_target": "pods", "namespace": "default"}, config)

    out = capsys.readouterr().out
    assert "candidates discarded by id_pattern" in out
    assert "my-pod-bad-suffix" in out
