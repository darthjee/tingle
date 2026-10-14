"""constants.py — Immutable configuration for code_check js_complexity."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from code_check.docker_check.constants import Constants as DockerCheckConstants
from code_check.file_size.constants import Constants as FileSizeConstants


class Constants:
    """Immutable configuration: thresholds, excludes, extensions and the image."""

    # Default thresholds on the file's (rounded) FTA score
    DEFAULT_WARN: ClassVar[float] = 50
    DEFAULT_ERROR: ClassVar[float] = 60
    DEFAULT_CRITICAL: ClassVar[float] = 75

    # --details given without N: show this many functions per file
    DEFAULT_DETAILS: ClassVar[int] = 5

    # file_size's default excludes plus JS tooling output directories
    DEFAULT_EXCLUDES: ClassVar[list[str]] = [
        *FileSizeConstants.DEFAULT_EXCLUDES,
        ".turbo", ".svelte-kit", ".output", ".vercel", ".parcel-cache", "storybook-static",
    ]

    # Core JavaScript/TypeScript extensions (compared case-insensitively)
    EXTENSIONS: ClassVar[list[str]] = [
        ".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx",
    ]

    # Single-file components (compared case-insensitively): the image analyses
    # their <script> blocks and Astro frontmatter only. No skip rule applies.
    SFC_EXTENSIONS: ClassVar[list[str]] = [".vue", ".svelte", ".astro"]

    # TypeScript declaration files, always skipped (matched on the lower-case name)
    DECLARATION_SUFFIXES: ClassVar[tuple[str, ...]] = (".d.ts", ".d.mts", ".d.cts")

    # Minified bundles, skipped by default unless no_default_excludes
    # (matched on the lower-case name)
    MINIFIED_SUFFIXES: ClassVar[tuple[str, ...]] = (".min.js", ".min.mjs", ".min.cjs")

    # Docker image repository; the default tag is the tingle version
    IMAGE_REPO: ClassVar[str] = "darthjee/tingle_js_complexity"

    # Runtime source of truth for the tingle version (from the repo root)
    VERSION_FILE: ClassVar[Path] = DockerCheckConstants.VERSION_FILE
