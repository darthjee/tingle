"""docker_runner.py — Run RubyCritic in its Docker image.

`DockerRunner` checks that Docker is usable (`preflight`), pulls the image
when it is missing (`ensure_image`), runs the container with the selected
files on stdin (`run`) and turns a failed container run into an error
(`check_outcome`). Every failure raises `RubycriticError` with the
user-facing message. Commands are list-form, never through a shell.
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess  # nosec B404 - fixed `docker` binary, list-form args, no shell
import sys
from pathlib import Path

from code_check.palette import Palette
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.errors import RubycriticError

DOCKER = "docker"


def decode(data: bytes | None) -> str:
    """Decode container output as UTF-8, replacing invalid bytes."""
    return (data or b"").decode("utf-8", errors="replace")


def write_stderr(proc: subprocess.CompletedProcess) -> None:
    """Pass the container's stderr through to tingle's stderr."""
    text = decode(proc.stderr)
    if text:
        sys.stderr.write(text)
        sys.stderr.flush()


class DockerRunner:
    """Run the RubyCritic image with Docker."""

    def __init__(self, image: str):
        """Store the resolved `image`."""
        self.image = image

    def preflight(self) -> None:
        """Check that `docker` is on PATH and that the daemon answers `docker info`."""
        if shutil.which(DOCKER) is None:
            raise RubycriticError(
                "docker not found on PATH; tingle code_check rubycritic needs Docker "
                "to run RubyCritic"
            )
        try:
            result = subprocess.run(  # nosec B603 - fixed binary, list-form args, no shell
                [DOCKER, "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=Constants.DOCKER_INFO_TIMEOUT,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            result = None
        if result is None or result.returncode != 0:
            raise RubycriticError(
                "the Docker daemon is not responding (docker info failed); "
                "start Docker and retry"
            )

    def ensure_image(self) -> None:
        """Pull the image when `docker image inspect` does not find it locally."""
        if self._quiet_ok([DOCKER, "image", "inspect", self.image]):
            return
        err = Palette(sys.stderr)
        print(f"{err.DIM}Pulling {self.image} ...{err.RESET}", file=sys.stderr)
        if not self._pull():
            raise RubycriticError(f"could not pull image {self.image}")

    def run(self, root: Path, lines: list[str]) -> subprocess.CompletedProcess:
        """Run the container on `root`, sending `lines` on stdin; capture its output."""
        stdin = "".join(f"{line}\n" for line in lines).encode("utf-8")
        try:
            return subprocess.run(  # nosec B603 - fixed binary, list-form args, no shell
                self.run_args(root),
                input=stdin,
                capture_output=True,
                check=False,
            )
        except OSError as exc:
            raise RubycriticError(f"could not run docker: {exc}") from exc

    def run_args(self, root: Path) -> list[str]:
        """Return the exact `docker run` argument list for the mount `root`."""
        return [
            DOCKER, "run", "--rm", "-i", "--pull", "never", "--network", "none",
            "--security-opt", "no-new-privileges",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{root}:/src:ro",
            "-w", "/src",
            self.image,
        ]

    def check_outcome(self, proc: subprocess.CompletedProcess, root: Path) -> None:
        """Raise for a non-zero container status, after passing its stderr through."""
        status = proc.returncode
        if status == 0:
            return
        write_stderr(proc)
        stderr = decode(proc.stderr).lower()
        if status == 125 and any(m in stderr for m in Constants.MOUNT_ERROR_MARKERS):
            raise RubycriticError(
                f"Docker could not mount {root}; on Docker Desktop, share it (or a parent "
                "folder) under Settings > Resources > File sharing, then retry"
            )
        raise RubycriticError(f"RubyCritic failed in {self.image} (exit {status})")

    @staticmethod
    def _quiet_ok(args: list[str]) -> bool:
        """Run `args` with output discarded; return True on exit status 0."""
        try:
            result = subprocess.run(  # nosec B603 - fixed binary, list-form args, no shell
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError:
            return False
        return result.returncode == 0

    def _pull(self) -> bool:
        """Run `docker pull`, showing its progress on stderr; return True on success."""
        args = [DOCKER, "pull", self.image]
        sys.stderr.flush()
        try:
            fileno = sys.stderr.fileno()
        except (AttributeError, OSError, ValueError, io.UnsupportedOperation):
            fileno = None
        try:
            if fileno is None:
                result = subprocess.run(  # nosec B603 - fixed binary, list-form args, no shell
                    args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
                )
                sys.stderr.write(decode(result.stdout))
            else:
                result = subprocess.run(  # nosec B603 - fixed binary, list-form args, no shell
                    args, stdout=fileno, stderr=fileno, check=False
                )
        except OSError:
            return False
        return result.returncode == 0
