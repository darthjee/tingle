"""Unit tests for code_check.docker_check.docker_runner (Docker is never run)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_check.docker_check import docker_runner
from code_check.docker_check.docker_runner import DockerRunner, decode, write_stderr
from code_check.docker_check.errors import DockerCheckError

IMAGE = "darthjee/tingle_other:1.0"


class OtherError(DockerCheckError):
    """A check-specific error class, to show the runner raises the one it is given."""


class Recorder:
    """Stand-in for `subprocess.run`: records calls and replays scripted results."""

    def __init__(self, *results):
        self.calls = []
        self._results = list(results)

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        result = self._results.pop(0) if self._results else 0
        if isinstance(result, BaseException):
            raise result
        if isinstance(result, int):
            return SimpleNamespace(returncode=result, stdout=b"", stderr=b"")
        return result


@pytest.fixture
def which(monkeypatch):
    found = {"path": "/usr/bin/docker"}
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: found["path"])
    return found


def _install(monkeypatch, *results):
    recorder = Recorder(*results)
    monkeypatch.setattr(docker_runner.subprocess, "run", recorder)
    return recorder


def _runner(image=IMAGE):
    return DockerRunner(
        image, error_class=OtherError, command="tingle code_check other", tool="OtherTool"
    )


# --- preflight ---------------------------------------------------------------------


def test_preflight_ok(monkeypatch, which):
    recorder = _install(monkeypatch, 0)

    _runner().preflight()

    args, kwargs = recorder.calls[0]
    assert args == ["docker", "info"]
    assert kwargs["timeout"] == 30


def test_preflight_docker_missing_uses_command_and_tool(monkeypatch, which):
    which["path"] = None
    recorder = _install(monkeypatch)

    with pytest.raises(OtherError) as exc_info:
        _runner().preflight()

    assert exc_info.value.message == (
        "docker not found on PATH; tingle code_check other needs Docker to run OtherTool"
    )
    assert recorder.calls == []


@pytest.mark.parametrize(
    "result",
    [1, subprocess.TimeoutExpired(["docker", "info"], 30), OSError("boom")],
    ids=["non-zero", "timeout", "oserror"],
)
def test_preflight_daemon_not_responding(monkeypatch, which, result):
    _install(monkeypatch, result)

    with pytest.raises(OtherError) as exc_info:
        _runner().preflight()

    assert exc_info.value.message == (
        "the Docker daemon is not responding (docker info failed); start Docker and retry"
    )


# --- ensure_image ------------------------------------------------------------------


def test_ensure_image_present_does_not_pull(monkeypatch, capsys):
    recorder = _install(monkeypatch, 0)

    _runner().ensure_image()

    assert [args for args, _ in recorder.calls] == [["docker", "image", "inspect", IMAGE]]
    assert capsys.readouterr().err == ""


def test_ensure_image_pulls_when_missing(monkeypatch, capsys):
    pulled = SimpleNamespace(returncode=0, stdout=b"pull progress\n", stderr=b"")
    recorder = _install(monkeypatch, 1, pulled)

    _runner().ensure_image()

    assert recorder.calls[1][0] == ["docker", "pull", IMAGE]
    err = capsys.readouterr().err
    assert f"Pulling {IMAGE} ..." in err
    assert "pull progress" in err


@pytest.mark.parametrize("result", [1, OSError("x")], ids=["non-zero", "oserror"])
def test_ensure_image_pull_failure(monkeypatch, capsys, result):
    _install(monkeypatch, 1, result)

    with pytest.raises(OtherError) as exc_info:
        _runner().ensure_image()

    assert exc_info.value.message == f"could not pull image {IMAGE}"


def test_ensure_image_inspect_oserror_pulls(monkeypatch, capsys):
    recorder = _install(monkeypatch, OSError("x"), 0)

    _runner().ensure_image()

    assert recorder.calls[1][0] == ["docker", "pull", IMAGE]


# --- run ---------------------------------------------------------------------------


def test_run_args_are_exact(tmp_path):
    assert _runner().run_args(tmp_path) == [
        "docker", "run", "--rm", "-i", "--pull", "never", "--network", "none",
        "--security-opt", "no-new-privileges",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{tmp_path}:/src:ro",
        "-w", "/src",
        IMAGE,
    ]


def test_run_sends_lines_on_stdin(monkeypatch, tmp_path):
    recorder = _install(monkeypatch, 0)

    _runner().run(tmp_path, ["a.js", "lib/é.ts"])

    args, kwargs = recorder.calls[0]
    assert args == _runner().run_args(tmp_path)
    assert kwargs["input"] == "a.js\nlib/é.ts\n".encode()
    assert kwargs["capture_output"] is True
    assert "shell" not in kwargs


def test_run_oserror(monkeypatch, tmp_path):
    _install(monkeypatch, OSError("no exec"))

    with pytest.raises(OtherError) as exc_info:
        _runner().run(tmp_path, ["a.js"])

    assert exc_info.value.message == "could not run docker: no exec"


# --- check_outcome -----------------------------------------------------------------


def _proc(status, stderr=b""):
    return SimpleNamespace(returncode=status, stdout=b"", stderr=stderr)


def test_check_outcome_success_is_silent(capsys):
    _runner().check_outcome(_proc(0, b"noise"), Path("/src"))

    assert capsys.readouterr().err == ""


def test_check_outcome_failure_uses_tool(capsys):
    with pytest.raises(OtherError) as exc_info:
        _runner().check_outcome(_proc(3, b"boom\n"), Path("/src"))

    assert exc_info.value.message == f"OtherTool failed in {IMAGE} (exit 3)"
    assert capsys.readouterr().err == "boom\n"


@pytest.mark.parametrize("marker", [b"Mounts Denied: x", b"path is not shared from the host"])
def test_check_outcome_mount_hint(capsys, marker):
    with pytest.raises(OtherError) as exc_info:
        _runner().check_outcome(_proc(125, marker), Path("/proj"))

    assert exc_info.value.message == (
        "Docker could not mount /proj; on Docker Desktop, share it (or a parent "
        "folder) under Settings > Resources > File sharing, then retry"
    )


def test_check_outcome_125_without_marker_is_generic(capsys):
    with pytest.raises(OtherError) as exc_info:
        _runner().check_outcome(_proc(125, b"other"), Path("/proj"))

    assert exc_info.value.message == f"OtherTool failed in {IMAGE} (exit 125)"


# --- decode / write_stderr ---------------------------------------------------------


def test_decode_replaces_invalid_bytes():
    assert decode(b"ok\xff") == "ok�"
    assert decode(None) == ""


def test_write_stderr_passes_text_through(capsys):
    write_stderr(_proc(1, b"err text"))
    write_stderr(_proc(1, b""))

    assert capsys.readouterr().err == "err text"
