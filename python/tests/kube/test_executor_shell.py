"""Unit tests for kube.executor.Kube._shell."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from kube.constants import Constants
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


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_aborts_when_aws_precheck_fails(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_check.return_value = (False, "Unable to locate credentials")
    config = _config(aws_profile="prod")

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_check.assert_called_once_with("prod")
    mock_list_pods.assert_not_called()
    mock_exec.assert_not_called()
    out = capsys.readouterr().out
    assert (
        "kube shell: AWS credential check failed for profile 'prod': "
        "Unable to locate credentials"
    ) in out
    assert "environment" not in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_single_match_resolves_and_execs(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [_pod("my-pod-aaaaaaaaaa", "2024-01-01T00:00:00Z")],
        None,
    )
    mock_get_pod.return_value = (
        {"status": {"phase": "Running"}},
        None,
    )
    mock_exec.return_value = (True, None)
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
        shell="bash",  # nosec B604 - mock config value; exec_shell is patched, no real subprocess call
    )

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_list_pods.assert_called_once_with("prod-default-ns")
    mock_get_pod.assert_called_once_with("prod-default-ns", "my-pod-aaaaaaaaaa")
    mock_exec.assert_called_once_with("prod-default-ns", "my-pod-aaaaaaaaaa", "bash")
    out = capsys.readouterr().out
    assert "warning" not in out.lower()


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_warns_when_pod_alias_namespace_conflicts_with_argument(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [_pod("app-aaaaaaaaaa", "2024-01-01T00:00:00Z")],
        None,
    )
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(
        namespaces={"prod": {"app": "prod-app-ns", "db": "prod-db-ns"}},
        pods={
            "prod": {
                "app": {"prefix": "app-", "namespace": "app"},
                "db": {"prefix": "db-", "namespace": "db"},
            }
        },
        pod_id_pattern=r"^[a-z0-9]{10}$",
        shell="bash",  # nosec B604 - mock config value; exec_shell is patched, no real subprocess call
    )

    Kube._shell({"namespace_alias": "db", "pod_alias": "app"}, config)

    mock_list_pods.assert_called_once_with("prod-db-ns")
    mock_exec.assert_called_once_with("prod-db-ns", "app-aaaaaaaaaa", "bash")
    out = capsys.readouterr().out
    assert "warning" in out.lower()
    assert "app" in out
    assert "db" in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_pass_through_pod_alias_uses_literal_pod_name(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(namespaces={"prod": {"default": "prod-default-ns"}})

    Kube._shell(
        {"namespace_alias": "default", "pod_alias": "literal-pod-name"}, config
    )

    mock_list_pods.assert_not_called()
    mock_get_pod.assert_called_once_with("prod-default-ns", "literal-pod-name")
    mock_exec.assert_called_once_with("prod-default-ns", "literal-pod-name", Constants.DEFAULT_SHELL)
    out = capsys.readouterr().out
    assert "not found in configured pods" in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_zero_matches_prints_error_and_suggestions(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
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

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_get_pod.assert_not_called()
    mock_exec.assert_not_called()
    out = capsys.readouterr().out
    assert "no pods matched" in out
    assert "my-pod-bad-suffix" in out


@patch("kube.executor.prompt_pod_choice")
@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_multiple_matches_prompts_for_choice(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, mock_prompt, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    pod_a = _pod("my-pod-aaaaaaaaaa", "2024-01-01T00:00:00Z")
    pod_b = _pod("my-pod-bbbbbbbbbb", "2024-01-02T00:00:00Z")
    mock_list_pods.return_value = ([pod_a, pod_b], None)
    mock_prompt.return_value = pod_b
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_prompt.assert_called_once_with([pod_a, pod_b])
    mock_get_pod.assert_called_once_with("prod-default-ns", "my-pod-bbbbbbbbbb")
    mock_exec.assert_called_once_with(
        "prod-default-ns", "my-pod-bbbbbbbbbb", Constants.DEFAULT_SHELL
    )


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_non_running_pod_warns_but_still_execs(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [_pod("my-pod-aaaaaaaaaa", "2024-01-01T00:00:00Z")],
        None,
    )
    mock_get_pod.return_value = ({"status": {"phase": "Pending"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_exec.assert_called_once_with(
        "prod-default-ns", "my-pod-aaaaaaaaaa", Constants.DEFAULT_SHELL
    )
    out = capsys.readouterr().out
    assert "warning" in out.lower()


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
def test_shell_get_pod_error_aborts_before_exec(
    mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_check.return_value = (True, None)
    mock_detect.return_value = "prod"
    mock_list_pods.return_value = (
        [_pod("my-pod-aaaaaaaaaa", "2024-01-01T00:00:00Z")],
        None,
    )
    mock_get_pod.return_value = (None, 'pods "my-pod-aaaaaaaaaa" not found')
    config = _config(
        namespaces={"prod": {"default": "prod-default-ns"}},
        pods={"prod": {"api": {"prefix": "my-pod-"}}},
        pod_id_pattern=r"^[a-z0-9]{10}$",
    )

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_exec.assert_not_called()
    out = capsys.readouterr().out
    assert 'pods "my-pod-aaaaaaaaaa" not found' in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_shell_env_mode_prints_notice_and_skips_profile(
    mock_source, mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_source.return_value = "env"
    mock_check.return_value = (True, None)
    mock_list_pods.return_value = ([], None)
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(aws_profile="prod")

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_check.assert_called_once_with(None)
    out = capsys.readouterr().out
    assert "kube: using AWS credentials from environment (aws_profile ignored)" in out
    assert "warning" not in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_shell_partial_mode_warns_and_falls_back_to_profile(
    mock_source, mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_source.return_value = "partial"
    mock_check.return_value = (True, None)
    mock_list_pods.return_value = ([], None)
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(aws_profile="prod")

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_check.assert_called_once_with("prod")
    out = capsys.readouterr().out
    assert (
        "kube: warning: incomplete AWS environment credentials "
        "(need both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY); "
        "falling back to profile 'prod'"
    ) in out
    assert "kube: using AWS credentials from environment (aws_profile ignored)" not in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_shell_profile_mode_prints_no_notice(
    mock_source, mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_source.return_value = "profile"
    mock_check.return_value = (True, None)
    mock_list_pods.return_value = ([], None)
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(aws_profile="prod")

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_check.assert_called_once_with("prod")
    out = capsys.readouterr().out
    assert "kube: using AWS credentials from environment (aws_profile ignored)" not in out
    assert "incomplete AWS environment credentials" not in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_shell_env_mode_failure_mentions_environment_credentials(
    mock_source, mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_source.return_value = "env"
    mock_check.return_value = (False, "Unable to locate credentials")
    mock_list_pods.return_value = ([], None)
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(aws_profile="prod")

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_check.assert_called_once_with(None)
    mock_list_pods.assert_not_called()
    out = capsys.readouterr().out
    assert (
        "kube shell: AWS credential check failed for environment credentials: "
        "Unable to locate credentials"
    ) in out


@patch("kube.executor.exec_shell")
@patch("kube.executor.get_pod")
@patch("kube.executor.list_pods")
@patch("kube.executor.detect_active_scope")
@patch("kube.executor.check_aws_credentials")
@patch("kube.executor.detect_credential_source")
def test_shell_partial_mode_failure_mentions_profile(
    mock_source, mock_check, mock_detect, mock_list_pods, mock_get_pod, mock_exec, capsys
):
    mock_source.return_value = "partial"
    mock_check.return_value = (False, "Unable to locate credentials")
    mock_list_pods.return_value = ([], None)
    mock_get_pod.return_value = ({"status": {"phase": "Running"}}, None)
    mock_exec.return_value = (True, None)
    config = _config(aws_profile="prod")

    Kube._shell({"namespace_alias": "default", "pod_alias": "api"}, config)

    mock_check.assert_called_once_with("prod")
    mock_list_pods.assert_not_called()
    out = capsys.readouterr().out
    assert (
        "kube shell: AWS credential check failed for profile 'prod': "
        "Unable to locate credentials"
    ) in out
