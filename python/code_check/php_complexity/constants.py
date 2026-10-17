"""constants.py — Immutable configuration for code_check php_complexity."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from code_check.docker_check.constants import Constants as DockerCheckConstants
from code_check.file_size.constants import Constants as FileSizeConstants


class Constants:
    """Immutable configuration: thresholds, excludes, extensions and the image."""

    # Default thresholds on the file's total CCN
    DEFAULT_WARN: ClassVar[float] = 20
    DEFAULT_ERROR: ClassVar[float] = 40
    DEFAULT_CRITICAL: ClassVar[float] = 60

    # file_size's default excludes plus PHP framework output directories
    DEFAULT_EXCLUDES: ClassVar[list[str]] = [
        *FileSizeConstants.DEFAULT_EXCLUDES, "var", "storage", ".phpunit.cache",
    ]

    # PHP source extension (compared case-insensitively)
    EXTENSIONS: ClassVar[list[str]] = [".php"]

    # Blade templates, always skipped (matched on the lower-case name)
    BLADE_SUFFIX: ClassVar[str] = ".blade.php"

    # Directory segment pair skipped by default (Laravel's compiled cache)
    BOOTSTRAP_CACHE: ClassVar[tuple[str, str]] = ("bootstrap", "cache")

    # Docker image repository; the default tag is the tingle version
    IMAGE_REPO: ClassVar[str] = "darthjee/tingle_php_complexity"

    # Runtime source of truth for the tingle version (from the repo root)
    VERSION_FILE: ClassVar[Path] = DockerCheckConstants.VERSION_FILE
