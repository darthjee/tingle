"""constants.py — Immutable configuration for code_check rubycritic."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from code_check.file_size.constants import Constants as FileSizeConstants


class Constants:
    """Immutable configuration: thresholds, excludes, image and RubyCritic details."""

    # Default thresholds on the file's total Flog complexity
    DEFAULT_WARN: ClassVar[float] = 100
    DEFAULT_ERROR: ClassVar[float] = 200
    DEFAULT_CRITICAL: ClassVar[float] = 400

    # Methods shown per file by `--details` given without a value
    DEFAULT_DETAILS: ClassVar[int] = 5

    # file_size's default excludes plus Ruby-specific directories
    DEFAULT_EXCLUDES: ClassVar[list[str]] = [
        *FileSizeConstants.DEFAULT_EXCLUDES, "tmp", "log", ".bundle",
    ]

    # Only Ruby files are analysed
    EXTENSIONS: ClassVar[list[str]] = [".rb"]

    # Docker image repository; the default tag is the tingle version
    IMAGE_REPO: ClassVar[str] = "darthjee/tingle_rubycritic"

    # Runtime source of truth for the tingle version (from the repo root)
    VERSION_FILE: ClassVar[Path] = (
        Path(__file__).resolve().parents[3] / "shell" / "linux" / "VERSION"
    )

    # Seconds to wait for `docker info`
    DOCKER_INFO_TIMEOUT: ClassVar[int] = 30

    # Smell types that come from Flay/Flog, not Reek (not counted as smells)
    NON_REEK_SMELL_TYPES: ClassVar[tuple[str, ...]] = (
        "DuplicateCode", "HighComplexity", "VeryHighComplexity",
    )

    # Container stderr fragments (lower-case) that mean a Docker mount failure
    MOUNT_ERROR_MARKERS: ClassVar[tuple[str, ...]] = (
        "mounts denied", "not shared from the host",
    )
