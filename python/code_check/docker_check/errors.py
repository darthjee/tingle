"""errors.py — The base error raised by the docker_check helpers."""

from __future__ import annotations


class DockerCheckError(Exception):
    """A failure carrying the user-facing message (printed as `Error: <message>`)."""

    def __init__(self, message: str):
        """Store the user-facing `message`."""
        super().__init__(message)
        self.message = message
