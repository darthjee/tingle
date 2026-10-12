"""errors.py — The error raised by the rubycritic helpers."""

from __future__ import annotations

from code_check.docker_check.errors import DockerCheckError


class RubycriticError(DockerCheckError):
    """A failure carrying the user-facing message (printed as `Error: <message>`)."""
