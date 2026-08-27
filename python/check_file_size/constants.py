"""constants.py — Immutable configuration for check_file_size."""

from __future__ import annotations

from typing import ClassVar


class Constants:
    """Immutable configuration: colors, exclusions, binary extensions."""

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    # Default directories to exclude
    DEFAULT_EXCLUDES: ClassVar[list[str]] = [
        "node_modules", "dist", "build", ".git", "vendor",
        "third_party", ".next", "__pycache__", ".cache",
        "coverage", ".nuxt", "out", "target",
    ]

    # Binary file extensions — skipped automatically
    BINARY_EXTENSIONS: ClassVar[set[str]] = {
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
        ".tiff", ".tif", ".raw", ".heic", ".avif",
        # Videos
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv",
        # Audio
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
        # Binary documents
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        # Archives
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        # Executables and libraries
        ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".class", ".jar",
        ".war", ".pyc", ".pyo", ".wasm",
        # Binary fonts
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        # Databases
        ".db", ".sqlite", ".sqlite3", ".mdb",
        # Other
        ".dat", ".pak", ".bundle", ".min.js", ".min.css",
        ".lock", ".map",
    }

    # Default thresholds (in lines)
    DEFAULT_WARN = 300
    DEFAULT_ERROR = 500
    DEFAULT_CRITICAL = 1000
