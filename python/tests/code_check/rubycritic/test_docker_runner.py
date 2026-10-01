"""Unit tests for code_check.rubycritic.docker_runner (Docker is never run)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_check.rubycritic import docker_runner
from code_check.rubycritic.docker_runner import DockerRunner, decode, write_stderr
from code_check.rubycritic.errors import RubycriticError

IMAGE = "tingle_rubycritic:dev"


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

    @property
    def argvs(self):
        return [args for args, _kwargs in self.calls]


@pytest.fixture
def which(monkeypatch):
    found = {"path": "/usr/bin/docker"}
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: found["path"])
    return found


def _install(monkeypatch, *results):
    recorder = Recorder(*results)
    monkeypatch.setattr(docker_runner.subprocess, "run", recorder)
    return recorder


# --- preflight ---------------------------------------------------------------------


def test_preflight_ok(monkeypatch, which):
    recorder = _install(monkeypatch, 0)

    DockerRunner(IMAGE).preflight()

    args, kwargs = recorder.calls[0]
    assert args == ["docker", "info"]
    assert kwargs["stdout"] is subprocess.DEVNULL
    assert kwargs["stderr"] is subprocess.DEVNULL
    assert kwargs["timeout"] == 30
    assert "shell" not in kwargs


def test_preflight_docker_missing(monkeypatch, which):
    which["path"] = None
    recorder = _install(monkeypatch)

    with pytest.raises(RubycriticError) as exc_info:
        DockerRunner(IMAGE).preflight()

    assert exc_info.value.message == (
        "docker not found on PATH; tingle code_check rubycritic needs Docker to run RubyCritic"
    )
    assert recorder.calls == []


@pytest.mark.parametrize(
    "result",
    [1, subprocess.TimeoutExpired(["docker", "info"], 30), OSError("boom")],
    ids=["non-zero", "timeout", "oserror"],
)
def test_preflight_daemon_not_responding(monkeypatch, which, result):
    _install(monkeypatch, result)

    with pytest.raises(RubycriticError) as exc_info:
        DockerRunner(IMAGE).preflight()

    assert exc_info.value.message == (
        "the Docker daemon is not responding (docker info failed); start Docker and retry"
    )


# --- ensure_image ------------------------------------------------------------------


def test_ensure_image_present_does_not_pull(monkeypatch, capsys):
    recorder = _install(monkeypatch, 0)

    DockerRunner(IMAGE).ensure_image()

    assert recorder.argvs == [["docker", "image", "inspect", IMAGE]]
    _args, kwargs = recorder.calls[0]
    assert kwargs["stdout"] is subprocess.DEVNULL
    assert kwargs["stderr"] is subprocess.DEVNULL
    assert capsys.readouterr().err == ""


def test_ensure_image_missing_pulls_with_progress_on_stderr(monkeypatch, capsys):
    pulled = SimpleNamespace(returncode=0, stdout=b"Pulled layer\n", stderr=None)
    recorder = _install(monkeypatch, 1, pulled)

    DockerRunner(IMAGE).ensure_image()

    assert recorder.argvs == [
        ["docker", "image", "inspect", IMAGE],
        ["docker", "pull", IMAGE],
    ]
    assert capsys.readouterr().err == f"Pulling {IMAGE} ...\nPulled layer\n"


def test_ensure_image_inspect_oserror_pulls(monkeypatch, capsys):
    recorder = _install(monkeypatch, OSError("x"), 0)

    DockerRunner(IMAGE).ensure_image()

    assert recorder.argvs[1] == ["docker", "pull", IMAGE]


def test_pull_uses_real_stderr_fd_when_available(monkeypatch):
    recorder = _install(monkeypatch, 1, 0)

    class FdStream:
        flushed = False

        def write(self, text):
            return len(text)

        def flush(self):
            FdStream.flushed = True

        def fileno(self):
            return 2

        def isatty(self):
            return False

    monkeypatch.setattr("sys.stderr", FdStream())

    DockerRunner(IMAGE).ensure_image()

    _args, kwargs = recorder.calls[1]
    assert kwargs["stdout"] == 2
    assert kwargs["stderr"] == 2
    assert FdStream.flushed


@pytest.mark.parametrize("result", [1, OSError("x")], ids=["non-zero", "oserror"])
def test_ensure_image_pull_failure(monkeypatch, capsys, result):
    _install(monkeypatch, 1, result)

    with pytest.raises(RubycriticError) as exc_info:
        DockerRunner(IMAGE).ensure_image()

    assert exc_info.value.message == f"could not pull image {IMAGE}"


# --- run ---------------------------------------------------------------------------


def test_run_args_are_exact(tmp_path):
    assert DockerRunner(IMAGE).run_args(tmp_path) == [
        "docker", "run", "--rm", "-i", "--pull", "never", "--network", "none",
        "--security-opt", "no-new-privileges",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{tmp_path}:/src:ro",
        "-w", "/src",
        IMAGE,
    ]


def test_run_sends_lines_on_stdin(monkeypatch, tmp_path):
    done = SimpleNamespace(returncode=0, stdout=b"{}", stderr=b"")
    recorder = _install(monkeypatch, done)

    proc = DockerRunner(IMAGE).run(tmp_path, ["a b.rb", "lib/é.rb"])

    assert proc is done
    args, kwargs = recorder.calls[0]
    assert args == DockerRunner(IMAGE).run_args(tmp_path)
    assert kwargs["input"] == "a b.rb\nlib/é.rb\n".encode()
    assert kwargs["capture_output"] is True
    assert "timeout" not in kwargs
    assert "shell" not in kwargs


def test_run_oserror(monkeypatch, tmp_path):
    _install(monkeypatch, OSError("exec format error"))

    with pytest.raises(RubycriticError, match="could not run docker: exec format error"):
        DockerRunner(IMAGE).run(tmp_path, ["a.rb"])


# --- check_outcome -----------------------------------------------------------------


def _proc(status, stderr=b""):
    return SimpleNamespace(returncode=status, stdout=b"", stderr=stderr)


def test_check_outcome_success_writes_nothing(capsys):
    DockerRunner(IMAGE).check_outcome(_proc(0, b"noise"), Path("/r"))

    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    "stderr",
    [
        b"docker: Error response from daemon: Mounts Denied: nope\n",
        b"The path /r is NOT SHARED FROM THE HOST and is not known to Docker.\n",
    ],
)
def test_check_outcome_mount_failure(capsys, stderr):
    with pytest.raises(RubycriticError) as exc_info:
        DockerRunner(IMAGE).check_outcome(_proc(125, stderr), Path("/r"))

    assert exc_info.value.message == (
        "Docker could not mount /r; on Docker Desktop, share it (or a parent folder) "
        "under Settings > Resources > File sharing, then retry"
    )
    assert capsys.readouterr().err == stderr.decode()


def test_check_outcome_125_without_marker(capsys):
    with pytest.raises(RubycriticError) as exc_info:
        DockerRunner(IMAGE).check_outcome(_proc(125, b"daemon error\n"), Path("/r"))

    assert exc_info.value.message == f"RubyCritic failed in {IMAGE} (exit 125)"
    assert capsys.readouterr().err == "daemon error\n"


@pytest.mark.parametrize("status", [1, 126, 127])
def test_check_outcome_other_failures_pass_stderr_through(capsys, status):
    with pytest.raises(RubycriticError) as exc_info:
        DockerRunner(IMAGE).check_outcome(_proc(status, b"boom \xff\n"), Path("/r"))

    assert exc_info.value.message == f"RubyCritic failed in {IMAGE} (exit {status})"
    assert capsys.readouterr().err == "boom �\n"


# --- helpers -----------------------------------------------------------------------


def test_decode_handles_none_and_bad_bytes():
    assert decode(None) == ""
    assert decode(b"a\xffb") == "a�b"


def test_write_stderr_empty_writes_nothing(capsys):
    write_stderr(_proc(1, b""))

    assert capsys.readouterr().err == ""
