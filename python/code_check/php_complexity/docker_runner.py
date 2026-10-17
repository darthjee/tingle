"""docker_runner.py — Run PDepend in its Docker image.

`DockerRunner` checks that Docker is usable (`preflight`), pulls the image
when it is missing (`ensure_image`), runs the container with the selected
files on stdin (`run`) and turns a failed container run into an error
(`check_outcome`). Every failure raises `PhpComplexityError` with the
user-facing message. Commands are list-form, never through a shell.

The logic lives in `code_check.docker_check.docker_runner`; this module binds
the php_complexity error class and message parameters. `shutil` and
`subprocess` stay importable from here for the tests that patch them.
"""

from __future__ import annotations

import shutil  # noqa: F401 - kept reachable as `docker_runner.shutil` for tests
import subprocess  # noqa: F401 # nosec B404 - kept reachable as `docker_runner.subprocess`

from code_check.docker_check import docker_runner as docker_check_runner
from code_check.docker_check.docker_runner import DOCKER, decode, write_stderr
from code_check.php_complexity.errors import PhpComplexityError

__all__ = ["DOCKER", "DockerRunner", "decode", "write_stderr"]

# The tingle command and the tool named in the tool-specific messages.
COMMAND = "tingle code_check php_complexity"
TOOL = "PDepend"


class DockerRunner(docker_check_runner.DockerRunner):
    """Run the php_complexity (PDepend) image with Docker."""

    def __init__(self, image: str):
        """Store the resolved `image`, binding the php_complexity error class and messages."""
        super().__init__(image, error_class=PhpComplexityError, command=COMMAND, tool=TOOL)
