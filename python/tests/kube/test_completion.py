"""Unit tests for kube.completion.complete."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.completion import complete


def _config(contexts=None, namespaces=None, pods=None, pass_through=False):
    config = MagicMock()
    config.pass_through = pass_through
    config.data = {
        "contexts": contexts or {},
        "namespaces": namespaces or {},
        "pods": pods or {},
    }
    return config


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_no_subcommand_returns_top_level_verbs(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()

    assert complete([""]) == ["switch", "list", "shell", "configure"]
    mock_config_cls.assert_not_called()
    mock_detect.assert_not_called()


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_partial_subcommand_still_returns_top_level_verbs(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()

    assert complete(["sw"]) == ["switch", "list", "shell", "configure"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_list_returns_targets_and_json_flag(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()
    mock_detect.return_value = None

    assert complete(["list", ""]) == ["namespace", "pods", "--json"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_list_pods_returns_namespace_flag(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()
    mock_detect.return_value = None

    assert complete(["list", "pods", ""]) == ["--namespace"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_list_json_before_pods_resolves_to_same_position(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()
    mock_detect.return_value = None

    assert complete(["list", "--json", "pods", ""]) == ["--namespace"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_list_pods_json_after_resolves_to_same_position(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()
    mock_detect.return_value = None

    assert complete(["list", "pods", "--json", ""]) == ["--namespace"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_switch_returns_configured_context_aliases(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config(contexts={"prod": "arn:1", "qa": "arn:2"})
    mock_detect.return_value = None

    assert sorted(complete(["switch", ""])) == ["prod", "qa"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_list_pods_namespace_flag_returns_scoped_namespace_aliases(
    mock_config_cls, mock_detect
):
    mock_config_cls.return_value = _config(
        namespaces={"prod": {"default": "prod-default-ns", "app": "prod-app-ns"}}
    )
    mock_detect.return_value = "prod"

    result = complete(["list", "pods", "--namespace", ""])

    assert sorted(result) == ["app", "default"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_shell_returns_scoped_namespace_aliases(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config(
        namespaces={"prod": {"default": "prod-default-ns"}}
    )
    mock_detect.return_value = "prod"

    assert complete(["shell", ""]) == ["default"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_shell_namespace_alias_returns_matching_pod_aliases_only(
    mock_config_cls, mock_detect
):
    mock_config_cls.return_value = _config(
        pods={
            "prod": {
                "app": {"prefix": "app-", "namespace": "app"},
                "db": {"prefix": "db-", "namespace": "db"},
                "shared": {"prefix": "shared-"},
            }
        }
    )
    mock_detect.return_value = "prod"

    result = complete(["shell", "app", ""])

    assert sorted(result) == ["app", "shared"]
    assert "db" not in result


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_configure_returns_targets(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()

    assert complete(["configure", ""]) == ["context", "namespace", "pod"]


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_configure_target_has_no_further_completion(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config()

    assert complete(["configure", "context", ""]) == []


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_pass_through_config_still_returns_static_candidates(
    mock_config_cls, mock_detect
):
    mock_config_cls.return_value = _config(pass_through=True)
    mock_detect.return_value = None

    assert complete(["list", ""]) == ["namespace", "pods", "--json"]
    assert complete(["switch", ""]) == []


@patch("kube.completion.scope.detect_active_scope")
@patch("kube.completion.KubeConfig")
def test_missing_kubectl_degrades_to_static_only(mock_config_cls, mock_detect):
    mock_config_cls.return_value = _config(
        namespaces={"prod": {"default": "prod-default-ns"}}
    )
    mock_detect.side_effect = FileNotFoundError("kubectl not found")

    assert complete(["shell", ""]) == []
    assert complete(["list", ""]) == ["namespace", "pods", "--json"]
