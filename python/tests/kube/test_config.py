"""Unit tests for kube.config.KubeConfig."""

from __future__ import annotations

import json

from kube.config import KubeConfig


def test_missing_config_file_falls_back_to_pass_through(tmp_path):
    missing = tmp_path / "config.json"

    config = KubeConfig(missing)

    assert config.pass_through is True
    assert config.data == {}
    assert "not found" in config.notice


def test_invalid_json_falls_back_to_pass_through(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("not valid json")

    config = KubeConfig(path)

    assert config.pass_through is True
    assert "invalid JSON" in config.notice


def test_non_object_config_falls_back_to_pass_through(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(["not", "an", "object"]))

    config = KubeConfig(path)

    assert config.pass_through is True
    assert "must be a JSON object" in config.notice


def test_missing_required_key_falls_back_to_pass_through(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"aws_profile": "prod"}))

    config = KubeConfig(path)

    assert config.pass_through is True
    assert "version" in config.notice


def test_object_key_with_wrong_type_falls_back_to_pass_through(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"version": 1, "contexts": "not-an-object"}))

    config = KubeConfig(path)

    assert config.pass_through is True
    assert "contexts" in config.notice


def test_pod_entry_missing_prefix_falls_back_to_pass_through(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"version": 1, "pods": {"prod": {"web": {"namespace": "default"}}}})
    )

    config = KubeConfig(path)

    assert config.pass_through is True
    assert "prefix" in config.notice


def test_valid_minimal_config_applies_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"version": 1}))

    config = KubeConfig(path)

    assert config.pass_through is False
    assert config.notice is None
    assert config.data == {
        "version": 1,
        "aws_profile": "default",
        "pod_id_pattern": "^[a-z0-9]{10}$",
        "shell": "bash",
        "contexts": {},
        "namespaces": {},
        "pods": {},
    }


def test_valid_config_keeps_explicit_values_over_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "aws_profile": "prod",
                "pod_id_pattern": "^[A-Z0-9]{8}$",
                "shell": "zsh",
                "contexts": {"prod": "arn:aws:eks:prod"},
                "namespaces": {"prod": {"web": "web-namespace"}},
                "pods": {"prod": {"web": {"prefix": "web-"}}},
            }
        )
    )

    config = KubeConfig(path)

    assert config.pass_through is False
    assert config.data["aws_profile"] == "prod"
    assert config.data["pod_id_pattern"] == "^[A-Z0-9]{8}$"
    assert config.data["shell"] == "zsh"
    assert config.data["contexts"] == {"prod": "arn:aws:eks:prod"}
    assert config.data["pods"]["prod"]["web"]["prefix"] == "web-"


def test_valid_pod_entry_with_optional_fields(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "pods": {
                    "prod": {
                        "web": {
                            "prefix": "web-",
                            "id_pattern": "^[a-z0-9]{10}$",
                            "namespace": "web-namespace",
                        }
                    }
                },
            }
        )
    )

    config = KubeConfig(path)

    assert config.pass_through is False
    assert config.data["pods"]["prod"]["web"]["id_pattern"] == "^[a-z0-9]{10}$"


def test_raw_reflects_unmodified_file_contents_without_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"version": 1}))

    config = KubeConfig(path)

    assert config.raw == {"version": 1}
    assert "aws_profile" not in config.raw


def test_raw_is_empty_when_file_missing(tmp_path):
    missing = tmp_path / "config.json"

    config = KubeConfig(missing)

    assert config.raw == {}


def test_validate_accepts_minimal_valid_draft(tmp_path):
    config = KubeConfig(tmp_path / "config.json")

    assert config.validate({"version": 1}) is None


def test_validate_rejects_missing_required_key(tmp_path):
    config = KubeConfig(tmp_path / "config.json")

    error = config.validate({"aws_profile": "prod"})

    assert error is not None
    assert "version" in error


def test_validate_rejects_malformed_pods_entry(tmp_path):
    config = KubeConfig(tmp_path / "config.json")

    error = config.validate({"version": 1, "pods": {"prod": {"web": {}}}})

    assert error is not None
    assert "prefix" in error


def test_save_writes_valid_draft_to_disk(tmp_path):
    path = tmp_path / "config.json"
    config = KubeConfig(path)

    error = config.save({"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}})

    assert error is None
    assert json.loads(path.read_text()) == {
        "version": 1,
        "contexts": {"prod": "arn:aws:eks:prod"},
    }


def test_save_creates_parent_directories_on_first_save(tmp_path):
    path = tmp_path / "nested" / "dir" / "config.json"
    config = KubeConfig(path)

    error = config.save({"version": 1})

    assert error is None
    assert path.exists()
    assert json.loads(path.read_text()) == {"version": 1}


def test_save_refuses_invalid_draft_and_leaves_existing_file_untouched(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"version": 1}))
    config = KubeConfig(path)

    error = config.save({"aws_profile": "prod"})

    assert error is not None
    assert "version" in error
    assert json.loads(path.read_text()) == {"version": 1}


def test_default_path_used_when_none_passed(tmp_path, monkeypatch):
    default_path = tmp_path / "config.json"
    default_path.write_text(json.dumps({"version": 1}))
    monkeypatch.setattr("kube.config.Constants.CONFIG_PATH", default_path)

    config = KubeConfig()

    assert config.pass_through is False
    assert config.data["version"] == 1
