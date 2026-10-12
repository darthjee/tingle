"""constants.py — Immutable configuration shared by the Docker-backed checks."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar


class Constants:
    """Immutable configuration: Docker timeouts, mount-error markers and the version file."""

    # Seconds to wait for `docker info`
    DOCKER_INFO_TIMEOUT: ClassVar[int] = 30

    # Container stderr fragments (lower-case) that mean a Docker mount failure
    MOUNT_ERROR_MARKERS: ClassVar[tuple[str, ...]] = (
        "mounts denied", "not shared from the host",
    )

    # Runtime source of truth for the tingle version (from the repo root)
    VERSION_FILE: ClassVar[Path] = (
        Path(__file__).resolve().parents[3] / "shell" / "linux" / "VERSION"
    )
