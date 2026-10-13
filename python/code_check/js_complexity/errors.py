"""errors.py — The error raised by the js_complexity helpers."""

from __future__ import annotations

from code_check.docker_check.errors import DockerCheckError


class JsComplexityError(DockerCheckError):
    """A failure carrying the user-facing message (printed as `Error: <message>`)."""
