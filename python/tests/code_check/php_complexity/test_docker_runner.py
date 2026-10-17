"""Unit tests for code_check.php_complexity.docker_runner (Docker is never run)."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_check.php_complexity import docker_runner
from code_check.php_complexity.docker_runner import DockerRunner, decode, write_stderr
from code_check.php_complexity.errors import PhpComplexityError

IMAGE = "tingle_php_complexity:dev"


def _proc(status, stderr=b""):
    return SimpleNamespace(returncode=status, stdout=b"", stderr=stderr)


def test_binds_error_class_command_and_tool():
    runner = DockerRunner(IMAGE)

    assert runner.image == IMAGE
    assert runner.error_class is PhpComplexityError
    assert runner.command == "tingle code_check php_complexity"
    assert runner.tool == "PDepend"


def test_preflight_docker_missing(monkeypatch):
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: None)

    with pytest.raises(PhpComplexityError) as exc_info:
        DockerRunner(IMAGE).preflight()

    assert exc_info.value.message == (
        "docker not found on PATH; tingle code_check php_complexity needs Docker to run PDepend"
    )


def test_preflight_daemon_not_responding(monkeypatch):
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr(
        docker_runner.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1)
    )

    with pytest.raises(PhpComplexityError) as exc_info:
        DockerRunner(IMAGE).preflight()

    assert exc_info.value.message == (
        "the Docker daemon is not responding (docker info failed); start Docker and retry"
    )


def test_pull_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        docker_runner.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout=b"", stderr=b""),
    )

    with pytest.raises(PhpComplexityError) as exc_info:
        DockerRunner(IMAGE).ensure_image()

    assert exc_info.value.message == f"could not pull image {IMAGE}"
    assert f"Pulling {IMAGE} ..." in capsys.readouterr().err


def test_run_args_are_exact(tmp_path):
    assert DockerRunner(IMAGE).run_args(tmp_path) == [
        "docker", "run", "--rm", "-i", "--pull", "never", "--network", "none",
        "--security-opt", "no-new-privileges",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{tmp_path}:/src:ro",
        "-w", "/src",
        IMAGE,
    ]


@pytest.mark.parametrize("status", [1, 125, 127])
def test_container_failure_message(capsys, status):
    with pytest.raises(PhpComplexityError) as exc_info:
        DockerRunner(IMAGE).check_outcome(_proc(status, b"boom\n"), Path("/r"))

    assert exc_info.value.message == f"PDepend failed in {IMAGE} (exit {status})"
    assert capsys.readouterr().err == "boom\n"


def test_mount_failure_hint(capsys):
    stderr = b"docker: Error response from daemon: Mounts denied: nope\n"

    with pytest.raises(PhpComplexityError) as exc_info:
        DockerRunner(IMAGE).check_outcome(_proc(125, stderr), Path("/r"))

    assert exc_info.value.message == (
        "Docker could not mount /r; on Docker Desktop, share it (or a parent folder) "
        "under Settings > Resources > File sharing, then retry"
    )
    assert capsys.readouterr().err == stderr.decode()


def test_success_writes_nothing(capsys):
    DockerRunner(IMAGE).check_outcome(_proc(0, b"noise"), Path("/r"))

    assert capsys.readouterr().err == ""


def test_reexported_helpers():
    assert decode(b"a\xffb") == "a�b"
    assert callable(write_stderr)
