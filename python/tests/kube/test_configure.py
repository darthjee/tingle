"""Unit tests for kube.configure (configure_context/namespace/pod)."""

from __future__ import annotations

from kube.configure import configure_context, configure_namespace, configure_pod


def _real_config(tmp_path, raw=None):
    from kube.config import KubeConfig

    path = tmp_path / "config.json"
    config = KubeConfig(path)
    config.raw = raw or {}
    return config, path


def _inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda *_args, **_kwargs: next(iterator))


# --- configure_context ---


def test_configure_context_create(tmp_path, monkeypatch, capsys):
    config, path = _real_config(tmp_path, raw={"version": 1})
    _inputs(monkeypatch, ["1", "prod", "arn:aws:eks:prod"])

    configure_context(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["contexts"] == {"prod": "arn:aws:eks:prod"}
    assert "saved" in capsys.readouterr().out


def test_configure_context_edit(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path, raw={"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}
    )
    path.write_text('{"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}')
    _inputs(monkeypatch, ["2", "1", "prod", "arn:aws:eks:prod-2"])

    configure_context(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["contexts"] == {"prod": "arn:aws:eks:prod-2"}


def test_configure_context_remove_cascades_namespaces_and_pods(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path,
        raw={
            "version": 1,
            "contexts": {"prod": "arn:aws:eks:prod"},
            "namespaces": {"prod": {"web": "web-ns"}},
            "pods": {"prod": {"api": {"prefix": "api-"}}},
        },
    )
    path.write_text("{}")
    _inputs(monkeypatch, ["3", "1", "y"])

    configure_context(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["contexts"] == {}
    assert saved["namespaces"] == {}
    assert saved["pods"] == {}


def test_configure_context_invalid_menu_choice_reprompts(tmp_path, monkeypatch):
    config, path = _real_config(tmp_path, raw={"version": 1})
    _inputs(monkeypatch, ["9", "1", "prod", "arn:aws:eks:prod"])

    configure_context(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["contexts"] == {"prod": "arn:aws:eks:prod"}


def test_configure_context_empty_input_aborts(tmp_path, monkeypatch, capsys):
    config, path = _real_config(tmp_path)
    _inputs(monkeypatch, [""])

    configure_context(config)

    assert not path.exists()
    assert "aborted" in capsys.readouterr().out


# --- configure_namespace ---


def test_configure_namespace_requires_existing_context(tmp_path, monkeypatch, capsys):
    config, path = _real_config(tmp_path)

    configure_namespace(config)

    assert not path.exists()
    assert "no context aliases configured" in capsys.readouterr().out


def test_configure_namespace_create(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path, raw={"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}
    )
    path.write_text('{"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}')
    _inputs(monkeypatch, ["1", "1", "web", "web-namespace"])

    configure_namespace(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["namespaces"] == {"prod": {"web": "web-namespace"}}


def test_configure_namespace_remove(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path,
        raw={
            "version": 1,
            "contexts": {"prod": "arn:aws:eks:prod"},
            "namespaces": {"prod": {"web": "web-namespace"}},
        },
    )
    path.write_text("{}")
    _inputs(monkeypatch, ["1", "3", "1"])

    configure_namespace(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["namespaces"] == {"prod": {}}


# --- configure_pod ---


def test_configure_pod_create_with_optional_fields_omitted_when_blank(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path, raw={"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}
    )
    path.write_text('{"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}')
    _inputs(monkeypatch, ["1", "1", "api", "api-", "", ""])

    configure_pod(config)

    import json

    saved = json.loads(path.read_text())
    pod = saved["pods"]["prod"]["api"]
    assert pod == {"prefix": "api-"}
    assert "id_pattern" not in pod
    assert "namespace" not in pod


def test_configure_pod_invalid_regex_reprompts(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path, raw={"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}
    )
    path.write_text('{"version": 1, "contexts": {"prod": "arn:aws:eks:prod"}}')
    _inputs(
        monkeypatch,
        ["1", "1", "api", "api-", "[unterminated", "^[a-z0-9]{10}$", ""],
    )

    configure_pod(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["pods"]["prod"]["api"]["id_pattern"] == "^[a-z0-9]{10}$"


def test_configure_pod_remove(tmp_path, monkeypatch):
    config, path = _real_config(
        tmp_path,
        raw={
            "version": 1,
            "contexts": {"prod": "arn:aws:eks:prod"},
            "pods": {"prod": {"api": {"prefix": "api-"}}},
        },
    )
    path.write_text("{}")
    _inputs(monkeypatch, ["1", "3", "1"])

    configure_pod(config)

    import json

    saved = json.loads(path.read_text())
    assert saved["pods"] == {"prod": {}}
